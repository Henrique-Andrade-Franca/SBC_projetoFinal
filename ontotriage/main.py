import os
import sys
from dotenv import load_dotenv

# garante que o modulo src seja encontrado
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.graph_rag import GraphRAGPipeline


def main():
    load_dotenv()
    ttl_path = "data/ontology.ttl"

    if not os.path.exists(ttl_path):
        print("Erro: Knowledge Graph não encontrado.")
        print("Execute 'python data/build_graph.py' primeiro para serializar o grafo.")
        return

    print("[Sistema] Inicializando OntoTriage...")
    print("[Sistema] Carregando Knowledge Graph e aplicando inferência OWL-RL...")
    pipeline = GraphRAGPipeline(ttl_path)

    print("\n" + "=" * 50)
    print(" OntoTriage: Sistema Especialista de Apoio")
    print("=" * 50)
    print("Digite 'sair' a qualquer momento para encerrar.\n")

    while True:
        try:
            user_input = input("Relate seus sintomas: ")
            if user_input.strip().lower() in ['sair', 'exit', 'quit']:
                print("Encerrando o sistema...")
                break

            if not user_input.strip():
                continue

            print("\n[GraphRAG] Extraindo entidades, consultando SPARQL e sintetizando...")
            resposta = pipeline.process_query(user_input)

            print("\n--- RESPOSTA FUNDAMENTADA ---")
            print(resposta)
            print("-" * 29 + "\n")

        except KeyboardInterrupt:
            print("\nEncerrando o sistema...")
            break
        except Exception as e:
            print(f"\n[Erro interno]: {e}\n")


if __name__ == "__main__":
    main()