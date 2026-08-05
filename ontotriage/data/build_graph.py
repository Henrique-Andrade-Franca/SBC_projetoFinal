import os
from rdflib import Graph, Namespace, Literal, URIRef
from rdflib.namespace import RDF, RDFS, OWL


def build_knowledge_graph() -> None:
    g = Graph()
    ONTO = Namespace("http://example.org/ontotriage#")
    PROV = Namespace("http://www.w3.org/ns/prov#")
    g.bind("onto", ONTO)
    g.bind("prov", PROV)

    # ontologia e proveniencia
    g.add((ONTO.OntoTriage, RDF.type, OWL.Ontology))
    g.add((ONTO.OntoTriage, RDFS.comment, Literal("Base de Conhecimento OntoTriage.")))

    # entidades de fonte (PROV-O) com descricoes rdfs:comment
    g.add((ONTO.Fonte_MS_Protocolos, RDF.type, PROV.Entity))
    g.add((ONTO.Fonte_MS_Protocolos, RDFS.label, Literal("Ministério da Saúde - Protocolos de Manejo Clínico")))
    g.add((ONTO.Fonte_MS_Protocolos, RDFS.comment, Literal(
        "Guia de Vigilância em Saúde e Protocolos de Manejo Clínico de Arboviroses e Doenças Respiratórias (Ministério da Saúde do Brasil).")))

    g.add((ONTO.Fonte_ANVISA_Bulario, RDF.type, PROV.Entity))
    g.add((ONTO.Fonte_ANVISA_Bulario, RDFS.label, Literal("ANVISA - Bulário Eletrônico")))
    g.add((ONTO.Fonte_ANVISA_Bulario, RDFS.comment, Literal(
        "Bulário Eletrônico da Agência Nacional de Vigilância Sanitária com restrições e contraindicações de medicamentos.")))

    # classes
    classes = ["Doenca", "Sintoma", "Medicamento", "CategoriaTerapeutica",
               "SintomaRespiratorio", "InfeccaoViral"]
    for cls in classes:
        g.add((ONTO[cls], RDF.type, OWL.Class))

    # hierarquias (inferencia)
    g.add((ONTO.SintomaRespiratorio, RDFS.subClassOf, ONTO.Sintoma))
    g.add((ONTO.InfeccaoViral, RDFS.subClassOf, ONTO.Doenca))

    # propriedades
    propriedades = {
        "apresentaSintoma": (ONTO.Doenca, ONTO.Sintoma),
        "indicadoPara": (ONTO.Medicamento, ONTO.Sintoma),
        "contraindicadoPara": (ONTO.Medicamento, ONTO.Doenca),
        "pertenceACategoria": (ONTO.Medicamento, ONTO.CategoriaTerapeutica)
    }
    for prop, (domain, range_) in propriedades.items():
        g.add((ONTO[prop], RDF.type, OWL.ObjectProperty))
        g.add((ONTO[prop], RDFS.domain, domain))
        g.add((ONTO[prop], RDFS.range, range_))

    # instancias - sintomas expandidos
    sintomas = {
        "Febre": ("Febre", ONTO.Sintoma),
        "DorDeCabeca": ("Dor de cabeça", ONTO.Sintoma),
        "DorRetroorbital": ("Dor atrás dos olhos", ONTO.Sintoma),
        "ManchasVermelhas": ("Manchas vermelhas no corpo", ONTO.Sintoma),
        "Artralgia": ("Dor intensa nas articulações", ONTO.Sintoma),
        "Tosse": ("Tosse", ONTO.SintomaRespiratorio),
        "Coriza": ("Coriza", ONTO.SintomaRespiratorio),
        "DificuldadeRespirar": ("Dificuldade para respirar", ONTO.SintomaRespiratorio)
    }
    for uri_suf, (label, tipo) in sintomas.items():
        g.add((ONTO[uri_suf], RDF.type, tipo))
        g.add((ONTO[uri_suf], RDFS.label, Literal(label)))

    # instancias - categorias terapeuticas
    categorias = {
        "AINE": "Anti-inflamatório Não Esteroidal",
        "Analgesico": "Analgésico e Antitérmico"
    }
    for uri_suf, label in categorias.items():
        g.add((ONTO[uri_suf], RDF.type, ONTO.CategoriaTerapeutica))
        g.add((ONTO[uri_suf], RDFS.label, Literal(label)))

    # instancias - medicamentos
    medicamentos = {
        "Paracetamol": ("Paracetamol", "Analgesico", ["Febre", "DorDeCabeca"]),
        "Dipirona": ("Dipirona", "Analgesico", ["Febre", "DorDeCabeca"]),
        "Ibuprofeno": ("Ibuprofeno", "AINE", ["Febre", "DorDeCabeca"]),
        "AAS": ("Ácido Acetilsalicílico", "AINE", ["Febre", "DorDeCabeca"])
    }
    for uri_suf, (label, cat, indicacoes) in medicamentos.items():
        g.add((ONTO[uri_suf], RDF.type, ONTO.Medicamento))
        g.add((ONTO[uri_suf], RDFS.label, Literal(label)))
        g.add((ONTO[uri_suf], ONTO.pertenceACategoria, ONTO[cat]))
        g.add((ONTO[uri_suf], PROV.wasDerivedFrom, ONTO.Fonte_ANVISA_Bulario))
        for ind in indicacoes:
            g.add((ONTO[uri_suf], ONTO.indicadoPara, ONTO[ind]))

    # instancias - doencas
    doencas = {
        "Dengue": ("Dengue", ["Febre", "DorDeCabeca", "DorRetroorbital", "ManchasVermelhas"]),
        "Zika": ("Zika Vírus", ["Febre", "DorDeCabeca", "ManchasVermelhas", "Artralgia"]),
        "Chikungunya": ("Chikungunya", ["Febre", "Artralgia", "DorDeCabeca"]),
        "Gripe": ("Gripe (Influenza)", ["Febre", "DorDeCabeca", "Tosse", "Coriza"]),
        "COVID19": ("COVID-19", ["Febre", "Tosse", "DificuldadeRespirar"])
    }

    for uri_suf, (label, s_list) in doencas.items():
        g.add((ONTO[uri_suf], RDF.type, ONTO.InfeccaoViral))
        g.add((ONTO[uri_suf], RDFS.label, Literal(label)))
        g.add((ONTO[uri_suf], PROV.wasDerivedFrom, ONTO.Fonte_MS_Protocolos))
        for s in s_list:
            g.add((ONTO[uri_suf], ONTO.apresentaSintoma, ONTO[s]))

    # regras de contraindicacao
    arboviroses = ["Dengue", "Zika", "Chikungunya"]
    aines = ["Ibuprofeno", "AAS"]
    for arb in arboviroses:
        for aine in aines:
            g.add((ONTO[aine], ONTO.contraindicadoPara, ONTO[arb]))

    # serializacao
    output_path = os.path.join(os.path.dirname(__file__), "ontology.ttl")
    g.serialize(destination=output_path, format="turtle")
    print(f"[OK] Grafo construído e serializado em: {output_path}")


if __name__ == "__main__":
    build_knowledge_graph()