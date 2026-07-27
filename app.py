import sys
from pipeline.retrieval.retriever import rag_pipeline

def main():
    print("==================================================")
    print("   NCAI CLASS 11 BIOLOGY RAG - TERMINAL INTERFACE ")
    print("==================================================")
    print("Type your question below. Type 'exit' or 'quit' to close.\n")

    while True:
        try:
            query = input("\n[Student Query] > ").strip()
            
            if not query:
                print("[!] Please enter a valid question.")
                continue
                
            if query.lower() in ["exit", "quit"]:
                print("[*] Exiting RAG Terminal. Goodbye!")
                break

            print("[*] Searching indexed textbooks and guides...")
            result = rag_pipeline.answer_query(query)

            print("\n--------------------------------------------------")
            print("ANS:")
            print(result["answer"])
            print("\n--- SOURCES USED ---")
            for src in result["sources"]:
                print(f"  • {src}")
            print("--------------------------------------------------")

        except KeyboardInterrupt:
            print("\n[*] Exiting RAG Terminal. Goodbye!")
            break
        except Exception as e:
            print(f"\n[X] Error occurred: {e}")

if __name__ == "__main__":
    main()