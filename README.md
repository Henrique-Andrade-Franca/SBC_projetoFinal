# OntoTriage: Sistema Especialista de Apoio à Triagem Clínica

Sistema especialista baseado em Knowledge Graph (RDF/OWL), inferência lógica (OWL-RL) e GraphRAG utilizando LLM. O domínio contempla doenças, sintomas, categorias terapêuticas e contraindicações medicamentosas estruturadas manualmente com base em dados oficiais do Ministério da Saúde e ANVISA.

## Arquitetura
1. **Base de Conhecimento (`data/ontology.ttl`)**: Versão serializada e legível do Knowledge Graph em formato Turtle, modelada com `rdflib` em RDF/RDFS/OWL. A proveniência é vinculada a cada entidade usando `prov:wasDerivedFrom`. 
2. **Motor de Inferência**: Utiliza `owlrl` para expandir a ontologia (ex: inferência de subclasses e tipos).
3. **GraphRAG**: O LLM atua na extração de entidades (NER). O sistema executa consultas SPARQL no grafo que recuperam os fatos, restrições e as fontes associadas às entidades recuperadas. O contexto resultante é enviado ao LLM, que sintetiza a resposta fundamentada.

## Reconstrução do Knowledge Graph

**Para reconstruir o grafo RDF/OWL:**
```bash
python data/build_graph.py
   ```
O script gera novamente o arquivo: `data/ontology.ttl`

Após isso, execute o sistema normalmente:
```bash
python main.py
   ```
## Requisitos
- Python 3.9+
- Chave de API do Google Gemini (`GEMINI_API_KEY`)

**O projeto fornece um arquivo .env.example com o formato esperado:**

``GEMINI_API_KEY=sua_chave_aqui``

`**Para configurar o ambiente localmente:** Faça uma cópia do arquivo .env.example e renomeie-a para ``.env``.
Substitua sua_chave_aqui pela sua chave de API do Google Gemini.

O sistema utiliza ``python-dotenv`` para carregar a variável GEMINI_API_KEY durante a execução.

## Instruções de Execução

1. **Instalação das dependências:**
```bash
pip install -r requirements.txt
   ```

2. **Configuração da chave de API:**

Configure o arquivo ``.env`` conforme descrito na seção de configuração do ambiente.

3. **Reconstrução do Knowledge Graph:**
```bash
python data/build_graph.py
   ```

4. **Execução do sistema:**
```bash
python main.py
   ```

Caso o arquivo ``data/ontology.ttl`` não exista, o sistema informará que o Knowledge Graph precisa ser construído antes da execução.

Durante a execução, informe os sintomas em linguagem natural. Para encerrar o sistema, digite: ``sair``
