# Fontes de Dados e Proveniência (Knowledge Graph)

O Knowledge Graph do OntoTriage é modelado manualmente através da curadoria de informações clínicas extraídas de fontes oficiais e confiáveis. 

A proveniência é modelada utilizando a propriedade `prov:wasDerivedFrom` da ontologia PROV-O para relacionar entidades do Knowledge Graph aos documentos oficiais utilizados durante a curadoria. Essas fontes de proveniência são recuperadas dinamicamente via SPARQL e enviadas ao LLM para fundamentar a resposta final.

## Fontes Oficiais Utilizadas

### 1. Ministério da Saúde (Brasil)
- **URI no Grafo:** `onto:Fonte_MS_Protocolos`
- **Descrição (`rdfs:comment`):** Guia de Vigilância em Saúde e Protocolos de Manejo Clínico de Arboviroses e Doenças Respiratórias (Ministério da Saúde do Brasil).
- **Entidades Vinculadas:** `Dengue`, `Zika`, `Chikungunya`, `Gripe`, `COVID19`.

### 2. Agência Nacional de Vigilância Sanitária (ANVISA)
- **URI no Grafo:** `onto:Fonte_ANVISA_Bulario`
- **Descrição (`rdfs:comment`):** Bulário Eletrônico da Agência Nacional de Vigilância Sanitária com restrições e contraindicações de medicamentos.
- **Entidades Vinculadas:** `Paracetamol`, `Dipirona`, `Ibuprofeno`, `AAS`.