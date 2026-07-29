import sys
import os
from PIL import Image
from pipeline.retrieval.retriever import rag_pipeline

# 1. Import the Class (Capital I and R)
from pipeline.retrieval.image_retriever import ImageRetriever

# 2. Instantiate it with a distinct variable name
img_retriever = ImageRetriever()

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

            # --- STEP 1: IMAGE RETRIEVAL CHECK ---
            image_result = img_retriever.retrieve_image(query)

            if image_result["status"] == "success":
                fig_data = image_result["data"][0]
                
                # Use .get() to prevent KeyErrors if the dictionary keys change
                match_type = fig_data.get('match_type', 'Direct Match')
                caption = fig_data.get('caption', 'Unknown Caption')
                
                print(f"\n[+] Image Match Found! ({match_type})")
                print(f"[*] Caption: {caption}")
                
                # SMART FETCH: Try all possible keys to guarantee we find the path
                img_path = fig_data.get('image') or fig_data.get('image_path') or fig_data.get('file_path')
                
                if img_path:
                    # Apply your folder rename fix
                    img_path = img_path.replace("figure1_output", "figure1_output - Copy")
                    
                    if os.path.exists(img_path):
                        print(f"[*] Opening image viewer...")
                        img = Image.open(img_path)
                        img.show()
                    else:
                        print(f"[!] Error: Image file missing at {img_path}")
                else:
                    # Print raw data if path is still missing so we can debug it
                    print(f"[!] Error: Path missing. Available data keys: {list(fig_data.keys())}")
                    print(f"Raw data: {fig_data}")

            # --- ADDED STEP: Catch strict missing figure requests ---
            elif "not found in the database" in image_result.get("message", ""):
                print(f"[-] {image_result['message']}")
                continue

            # --- STEP 2: FALLBACK TO TEXT RAG (Restored) ---
            else:
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