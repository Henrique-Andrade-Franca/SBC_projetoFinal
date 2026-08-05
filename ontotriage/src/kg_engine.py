import owlrl
from rdflib import Graph, Namespace
from typing import List, Dict


class KGEngine:
    def __init__(self, ttl_path: str):
        self.g = Graph()
        self.g.parse(ttl_path, format="turtle")
        self.onto_ns = Namespace("http://example.org/ontotriage#")
        self._apply_reasoning()

    def _apply_reasoning(self) -> None:
        # expande o grafo aplicando as regras logicas de RDFS e OWL
        owlrl.DeductiveClosure(owlrl.OWLRL_Semantics).expand(self.g)

    def get_all_symptoms(self) -> List[Dict[str, str]]:
        query = """
        PREFIX onto: <http://example.org/ontotriage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?id ?label WHERE {
            ?id a onto:Sintoma .
            ?id rdfs:label ?label .
        }
        """
        results = self.g.query(query)
        return [{"id": str(r.id), "label": str(r.label)} for r in results]

    def query_diseases_by_symptoms(self, symptom_uris: List[str]) -> List[Dict]:
        if not symptom_uris:
            return []

        uris_str = ", ".join(f"<{uri}>" for uri in symptom_uris)

        query = f"""
        PREFIX onto: <http://example.org/ontotriage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?doenca ?doencaLabel (COUNT(?sintoma) as ?matches)
        WHERE {{
            ?doenca a onto:Doenca ;
                    rdfs:label ?doencaLabel ;
                    onto:apresentaSintoma ?sintoma .
            FILTER(?sintoma IN ({uris_str}))
        }}
        GROUP BY ?doenca ?doencaLabel
        ORDER BY DESC(?matches)
        """
        return [{"uri": str(r.doenca), "label": str(r.doencaLabel), "matches": int(r.matches)}
                for r in self.g.query(query)]

    def query_disease_details(self, disease_uri: str) -> Dict[str, List]:
        # sintomas da doenca
        query_sintomas = f"""
        PREFIX onto: <http://example.org/ontotriage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?sintomaLabel WHERE {{
            <{disease_uri}> onto:apresentaSintoma ?sintoma .
            ?sintoma rdfs:label ?sintomaLabel .
        }}
        """
        sintomas = [str(r.sintomaLabel) for r in self.g.query(query_sintomas)]

        # contraindicacoes e proveniencia do medicamento
        query_contra = f"""
        PREFIX onto: <http://example.org/ontotriage#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        PREFIX prov: <http://www.w3.org/ns/prov#>
        SELECT ?medLabel ?catLabel ?fonteLabel WHERE {{
            ?med onto:contraindicadoPara <{disease_uri}> .
            ?med rdfs:label ?medLabel .
            OPTIONAL {{
                ?med onto:pertenceACategoria ?cat .
                ?cat rdfs:label ?catLabel .
            }}
            OPTIONAL {{
                ?med prov:wasDerivedFrom ?fonte .
                ?fonte rdfs:label ?fonteLabel .
            }}
        }}
        """
        contraindicacoes = []
        fontes_recuperadas = set()

        for r in self.g.query(query_contra):
            cat_info = f" (Categoria: {r.catLabel})" if r.catLabel else ""
            fonte_info = f" [Fonte: {r.fonteLabel}]" if r.fonteLabel else ""
            contraindicacoes.append(f"{r.medLabel}{cat_info}{fonte_info}")
            if r.fonteLabel:
                fontes_recuperadas.add(str(r.fonteLabel))

        # proveniencia da propria doenca
        query_fonte_doenca = f"""
        PREFIX prov: <http://www.w3.org/ns/prov#>
        PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
        SELECT ?fonteLabel ?fonteComment WHERE {{
            <{disease_uri}> prov:wasDerivedFrom ?fonte .
            ?fonte rdfs:label ?fonteLabel .
            OPTIONAL {{ ?fonte rdfs:comment ?fonteComment . }}
        }}
        """
        for r in self.g.query(query_fonte_doenca):
            label = str(r.fonteLabel)
            desc = f" ({r.fonteComment})" if r.fonteComment else ""
            fontes_recuperadas.add(f"{label}{desc}")

        return {
            "sintomas": sintomas,
            "contraindicacoes": contraindicacoes,
            "fontes": list(fontes_recuperadas)
        }