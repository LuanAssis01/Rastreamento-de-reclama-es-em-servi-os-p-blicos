import os
import json
import logging
import shutil
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings, OllamaLLM
from langchain.chains import RetrievalQA
from langchain_community.vectorstores import Chroma
from langchain.schema import Document
from langchain.prompts import PromptTemplate

# Configuração de logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Carregar o modelo LLM
llm = OllamaLLM(model="deepseek-r1:7b", request_timeout=5000.0, temperature=0.0)

# Carregar o modelo de embeddings
embeds_model = OllamaEmbeddings(model="deepseek-r1:7b")

# Verificar a dimensão dos embeddings
sample_embedding = embeds_model.embed_query("Teste de embedding")
logger.info(f"Dimensão do embedding: {len(sample_embedding)}")

# Caminho do arquivo JSON
JSON_FILE_PATH = "/home/adreyton/Documents/Luan/final_work/rastreamento/dataset/final-project.json"

## Template personalizado para forçar português
CUSTOM_PROMPT = PromptTemplate(
    template="""
    <system>
    Você é um assistente da prefeitura de Marabá-PA e voce deve analisar o documento carregado. Siga estas regras:
    1. Responda SEMPRE em português brasileiro
    2. Não gere blocos <think> ou raciocínios internos
    3. Seja direto e objetivo
    4. Use apenas o contexto fornecido
    5. Contexto: {context}
    </system>

    Pergunta: {question}
    Resposta:""",
    input_variables=["context", "question"]
)

# *************** ADICIONE ESTA SEÇÃO ***************
# Ler o arquivo JSON e processar os dados
def load_json_data(json_path):
    try:
        with open(json_path, "r", encoding="utf-8") as file:
            data = json.load(file)
        
        documents = []
        for idx, entry in enumerate(data):
            content = (f"Data: {entry.get('Data_Reclamacao')}\n"
                       f"Órgão: {entry.get('Órgão')}\n"
                       f"Local: {entry.get('Local')}\n"
                       f"Setor: {entry.get('Setor')}\n"
                       f"Status: {entry.get('Status')}.\nDescrição: {entry.get('Descrição')}")
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
# *****************************************************

# Criar e persistir o banco de vetores Chroma
PERSIST_DIRECTORY = "./chroma_db"
# Excluir diretório existente do Chroma
if os.path.exists(PERSIST_DIRECTORY):
    shutil.rmtree(PERSIST_DIRECTORY)

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

# *** ADICIONAR ESTA PARTE QUE ESTAVA FALTANDO ***
# Criar retriever
retriever = vector_store.as_retriever(search_kwargs={"k": 3})

# Configuração da cadeia QA modificada
qa_chain = RetrievalQA.from_chain_type(
    llm=llm,
    chain_type="stuff",
    retriever=retriever,  # Agora a variável existe
    return_source_documents=True,
    chain_type_kwargs={"prompt": CUSTOM_PROMPT}
)

# Função para processar perguntas
def ask(question):
    try:
        response = qa_chain.invoke({"query": f"Responda em português brasileiro: {question}"})
        answer = response.get('result', "Não encontrei informações relevantes.")
        return answer, response.get('source_documents', [])
    except Exception as e:
        return f"Erro: {str(e)}", None

# Interação com o usuário ajustada
if __name__ == "__main__":
    show_context = False  # Controle de exibição do contexto
    
    print("Sistema iniciado. Digite 'contexto' para mostrar/ocultar detalhes técnicos.")
    
    while True:
        user_question = input("\nUser: ").strip()
        
        # Comandos especiais
        if user_question.lower() == "contexto":
            show_context = not show_context
            status = "ATIVADO" if show_context else "DESATIVADO"
            print(f"\nModo contexto: {status}")
            continue
            
        if user_question.lower() in ["sair", "exit", "quit"]:
            print("Encerrando...")
            break
            
        if not user_question:
            continue
            
        answer, context = ask(user_question)
        
        # Exibe resposta principal
        print("\nResposta:", answer)
        
        # Exibe contexto apenas se solicitado
        if show_context and context:
            print("\n[Detalhes Técnicos]")
            for doc in context:
                print(f"- {doc.page_content[:150]}...")  # Exibe apenas trecho inicial