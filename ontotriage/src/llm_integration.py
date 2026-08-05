import os
import json
import google.generativeai as genai
from typing import List, Dict


class LLMClient:
    def __init__(self):
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY não configurada no ambiente (.env).")
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-3.6-flash')

    def extract_symptoms(self, text: str, valid_symptoms: List[Dict[str, str]]) -> List[str]:
        # realiza NER mapeando para a ontologia
        labels = [s['label'] for s in valid_symptoms]
        prompt = f"""
        Atue como um extrator de entidades clínicas.
        Texto do usuário: "{text}"
        Vocabulário controlado da ontologia: {labels}

        Sua única tarefa é mapear os sintomas descritos no texto para os termos exatos do vocabulário controlado.
        Retorne EXCLUSIVAMENTE um array JSON contendo as strings do vocabulário que estão presentes no texto.
        Exemplo de saída: ["Febre", "Dor atrás dos olhos"]
        """
        response = self.model.generate_content(prompt)
        try:
            clean_text = response.text.replace("```json", "").replace("```", "").strip()
            extracted_labels = json.loads(clean_text)
            return [s['id'] for s in valid_symptoms if s['label'] in extracted_labels]
        except Exception:
            return []

    def synthesize_response(self, user_text: str, kg_context: List[Dict]) -> str:
        # sintetiza a resposta final ancorada estritamente no KG e sua proveniencia
        prompt = f"""
        Você é o OntoTriage, um sistema especialista em triagem clínica.

        Relato do paciente: "{user_text}"

        Fatos e Proveniência recuperados via SPARQL do Knowledge Graph:
        {json.dumps(kg_context, indent=2, ensure_ascii=False)}

        Diretrizes estritas para a resposta:
        1. Responda de forma clara e objetiva.
        2. Liste as doenças recuperadas no contexto que correspondem aos sintomas relatados.
        3. DESTAQUE explicitamente qualquer medicamento que esteja sinalizado como "Contraindicado" no contexto.
        4. CITE EXPLICITAMENTE apenas as fontes constantes no campo 'Fontes_Oficiais_Consultadas' do contexto para fundamentar a resposta. Não presuma nem cite fontes externas que não estejam nesse campo.
        5. INCLUA OBRIGATORIAMENTE um aviso claro de que o sistema fornece apoio informacional à triagem e não substitui avaliação, diagnóstico ou prescrição médica presencial.
        """
        response = self.model.generate_content(prompt)
        return response.text