import unittest
import os
from src.kg_engine import KGEngine
from rdflib import URIRef


class TestKGEngine(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # garante que o grafo existe antes dos testes
        cls.ttl_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "ontology.ttl")
        if not os.path.exists(cls.ttl_path):
            from data.build_graph import build_knowledge_graph
            build_knowledge_graph()

        cls.engine = KGEngine(cls.ttl_path)

    def test_graph_loading(self):
        # testa se o KG foi carregado
        self.assertGreater(len(self.engine.g), 0, "O grafo não deveria estar vazio.")

    def test_owl_inference(self):
        # testa se a inferencia OWL-RL funcionou (rdfs:subClassOf)
        ONTO = self.engine.onto_ns
        from rdflib.namespace import RDF

        # tosse foi definida apenas como SintomaRespiratorio - a inferencia deve provar que tambem e Sintoma
        is_sintoma = (ONTO.Tosse, RDF.type, ONTO.Sintoma) in self.engine.g
        self.assertTrue(is_sintoma, "Inferência de rdfs:subClassOf falhou.")

    def test_get_all_symptoms(self):
        # testa a recuperacao de sintomas
        symptoms = self.engine.get_all_symptoms()
        self.assertGreater(len(symptoms), 0)
        labels = [s["label"] for s in symptoms]
        self.assertIn("Febre", labels)

    def test_query_diseases_by_symptoms(self):
        # testa a logica de match de doencas via SPARQL
        # enviando URIs de Febre e Dor atrás dos olhos
        symptom_uris = [
            str(self.engine.onto_ns.Febre),
            str(self.engine.onto_ns.DorRetroorbital)
        ]
        results = self.engine.query_diseases_by_symptoms(symptom_uris)
        self.assertTrue(any(r["label"] == "Dengue" for r in results))

    def test_query_disease_details(self):
        # testa a recuperacao de detalhes (sintomas e contraindicacoes)
        dengue_uri = str(self.engine.onto_ns.Dengue)
        details = self.engine.query_disease_details(dengue_uri)

        self.assertIn("Febre", details["sintomas"])
        # ibuprofeno e AAS devem estar contraindicados
        contraindicacoes_str = " ".join(details["contraindicacoes"])
        self.assertIn("Ibuprofeno", contraindicacoes_str)
        self.assertIn("Ácido Acetilsalicílico", contraindicacoes_str)


if __name__ == '__main__':
    unittest.main()