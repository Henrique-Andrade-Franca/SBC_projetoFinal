from src.kg_engine import KGEngine
from src.llm_integration import LLMClient


class GraphRAGPipeline:
    def __init__(self, ttl_path: str):
        self.kg = KGEngine(ttl_path)
        self.llm = LLMClient()

    def process_query(self, user_text: str) -> str:
        # recupera vocabulario base (subclasses via OWL inference)
        all_symptoms = self.kg.get_all_symptoms()

        # extrai as entidades via LLM
        extracted_uris = self.llm.extract_symptoms(user_text, all_symptoms)
        if not extracted_uris:
            return "Não foi possível identificar sintomas compatíveis com a nossa base de conhecimento oficial. Por favor, procure avaliação médica presencial."

        # consulta SPARQL para recuperar subgrafo
        diseases = self.kg.query_diseases_by_symptoms(extracted_uris)

        # monta o contexto fundamentado com proveniencia explicita
        kg_context = []
        for d in diseases:
            details = self.kg.query_disease_details(d['uri'])
            kg_context.append({
                "Doenca": d['label'],
                "Sintomas_Bateu_com_Relato": d['matches'],
                "Todos_Sintomas_da_Doenca": details['sintomas'],
                "Medicamentos_Contraindicados": details['contraindicacoes'],
                "Fontes_Oficiais_Consultadas": details['fontes']
            })

        # geracao de resposta fundamentada
        return self.llm.synthesize_response(user_text, kg_context)