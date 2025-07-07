import os
from langchain_community.document_loaders import TextLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_chroma import Chroma

source_path = "project/"
all_files_txt_path = "/mnt/1670554E70553629/Python-Comding/auto md/vector_db/all_files.txt"
persistent_directory = "/mnt/1670554E70553629/Python-Comding/auto md/vector_db/db"

skip_extensions = {'.exe', '.dll', '.bin', '.jpg', '.jpeg', '.png', '.gif', 
                   '.bmp', '.ico', '.zip', '.rar', '.7z', '.tar', '.gz',
                   '.mp3', '.mp4', '.avi', '.mkv', '.pdf', '.pyc'}

embeddings = OllamaEmbeddings(
    model="nomic-embed-text"
)

def create_all_files_txt():
    with open(all_files_txt_path, "w", encoding="utf-8") as f:
        for dirpath, dirnames, filenames in os.walk(source_path):
            # Skip __pycache__ directories
            if "__pycache__" in dirpath:
                continue 
                
            print(f"dir: {dirpath}")
            f.write(f"Current Directory: {dirpath}\n")
            f.write("=" * 50 + "\n")
            
            for filename in filenames:
                file_ext = os.path.splitext(filename)[1].lower()
                
                # Skip binary files - fix the logic here
                if file_ext in skip_extensions:
                    print(f"\tSkipping: {filename}")
                    continue
                    
                print(f"\tfile: {filename}")
                f.write(f"\nCurrent File: {filename}\n")
                f.write("-" * 30 + "\n")
                
                # Use os.path.join for proper path handling
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, "r", encoding="utf-8", errors="ignore") as sub_f:
                        content = sub_f.read()
                        f.write(content)
                        f.write(f"\n--- End of {filename} ---\n\n")
                except Exception as e:
                    error_msg = f"Error reading {filename}: {str(e)}\n\n"
                    print(f"\t{error_msg.strip()}")
                    f.write(error_msg)

def create_split_text():
    text_loader = TextLoader(all_files_txt_path)
    loaded_text = text_loader.load()

    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=2000,
        chunk_overlap=200
    )

    return text_splitter.split_documents(loaded_text)

def create_vectorstore():
    create_all_files_txt()
    try:
        vectorstore = Chroma.from_documents(
            documents=create_split_text(),
            embedding=embeddings,
            persist_directory=persistent_directory,
            collection_name="project"
        )
        print("Vector database created")
        return vectorstore
    except Exception as e:
        print(f"Error creating the vector database: {e}")
        raise

def create_retriever(use_existsing_db = False):
    if not use_existsing_db:
        vectorstore = create_vectorstore()
    else:
        print("using existing vector database")
        vectorstore = Chroma(
            persist_directory=persistent_directory,
            embedding_function=embeddings,
            collection_name="project"
        )   

    return vectorstore.as_retriever(
        search_type="similarity",
        search_kwargs={"k": 5}
    )
