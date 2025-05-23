FROM python:3.12

ARG SERVICE
ENV SERVICE=$SERVICE 

WORKDIR /app

# Copia arquivos de dependência
COPY pyproject.toml poetry.lock ./

# Instala dependências com Poetry
RUN pip install poetry && \
    poetry config virtualenvs.create false && \
    poetry install --no-root

# Copia o código da aplicação
COPY app/ ./app/
COPY streamlit_app/ ./streamlit_app/
COPY app/model/ ./model/
COPY app/static/ ./static/

# Usa shell como entrypoint e define comando dinamicamente com base no SERVICE
ENTRYPOINT ["sh", "-c"]
CMD ["if [ \"$SERVICE\" = \"api\" ]; then \
        uvicorn app.main:app --host 0.0.0.0 --port 8000; \
     elif [ \"$SERVICE\" = \"streamlit\" ]; then \
        streamlit run streamlit_app/app.py --server.port=8503 --server.address=0.0.0.0; \
     else \
        echo 'Serviço desconhecido: $SERVICE' && exit 1; \
     fi"]
