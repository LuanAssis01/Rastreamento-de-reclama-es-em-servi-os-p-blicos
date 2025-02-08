import os
import json
import logging
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA
from langchain.vectorstores import Chroma
from langchain.schema import Document

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar o modelo LLM
llm = OllamaLLM(model="deepseek-r1", request_timeout=5000.0, temperature=0.0)

# Carregar o modelo de embeddings
embeds_model = OllamaEmbeddings(model="deepseek-r1")

# Caminho do arquivo JSON
JSON_FILE_PATH = "/home/luan/rag/dataset.json"  # Atualize este caminho

# Ler o arquivo JSON e processar os dados
def load_json_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        documents = []
        for idx, entry in enumerate(data):
            content = "\n".join([f"{key}: {value}" for key, value in entry.items()])
            documents.append(Document(page_content=content, metadata={"index": idx}))

        return documents

    except FileNotFoundError:
        logger.error(f"Arquivo {json_path} não encontrado.")
        exit(1)
    except json.JSONDecodeError:
        logger.error(f"Erro ao decodificar JSON {json_path}.")
        exit(1)

# Carregar os documentos JSON
documents = load_json_data(JSON_FILE_PATH)

# Configurar divisão de texto
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=4000,
    chunk_overlap=20,
    length_function=len,
    add_start_index=True
)

# Criar chunks
chunks = text_splitter.split_documents(documents)

# Criar e persistir o banco de vetores Chroma
PERSIST_DIRECTORY = "./chroma_db"

try:
    vector_store = Chroma.from_documents(
        documents=chunks,
        embedding=embeds_model,
        persist_directory=PERSIST_DIRECTORY
    )
    logger.info("Banco de dados vetorial criado e persistido com sucesso.")
except Exception as e:
    logger.error(f"Erro ao criar o banco de dados vetorial: {e}")
    exit(1)

# Criar retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Criar cadeia de Pergunta & Resposta
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever
)

# Função para processar perguntas
def ask(question):
    try:
        # Recuperar documentos relevantes
        context = retriever.invoke(question)
        
        # Obter resposta do LLM
        response = qa_chain.invoke({"input_documents": context, "query": question})
        
        # Ajuste na extração da resposta
        answer = response.get('output_text', "Resposta não encontrada.")

        return answer, context  

    except Exception as e:
        return f"Erro ao processar a pergunta: {e}", None

# Interação com o usuário
if __name__ == "__main__":
    while True:
        user_question = input("\nUser: ")
        if user_question.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break
        
        answer, context = ask(user_question)
        
        print("\nResposta:", answer)
        
        if context:
            print("\nContexto utilizado:")
            for doc in context:
                print(doc.page_content)
