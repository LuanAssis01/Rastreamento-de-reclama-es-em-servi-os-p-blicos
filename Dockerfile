# Usar imagem base do Ubuntu
FROM ubuntu:24.04

# Definir variáveis de ambiente
ENV DEBIAN_FRONTEND=noninteractive

# Instalar dependências e o Ollama
RUN apt update && apt install -y curl && \
    curl -fsSL https://ollama.com/install.sh | sh && \
    apt clean && rm -rf /var/lib/apt/lists/*

# Definir o diretório de trabalho
WORKDIR /app

# Expor a porta do servidor
EXPOSE 11434

# Comando para rodar o servidor
ENTRYPOINT ["ollama", "serve"]

# Comando para garantir que o modelo esteja disponível (será executado quando o contêiner iniciar)
CMD ["ollama", "pull", "llama3.2:latest"]
