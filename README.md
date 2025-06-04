# MLET - Datathon - Projto 5 

## Estrutura do Projeto:
```
└── 📁APP_5
    └── 📁app
        └── 📁model
            └── modelo_stacking.pkl
        └── 📁static
            └── index.html
        └── main.py
    └── 📁data
        └── 📁applicants
            └── applicants.json
        └── 📁features
            └── features.csv
        └── 📁modelos
            └── modelo_stacking.pkl
        └── 📁prospects
            └── prospects.json
        └── 📁vagas
            └── vagas.json
        └── READ.ME.txt
    └── 📁streamlit_app
        └── app.py
        └── preprocess.py
    └── docker-compose.yml
    └── Dockerfile
    └── exploratory_analysis.ipynb
    └── feature_engineering.ipynb
    └── modelo.ipynb
    └── poetry.lock
    └── pyproject.toml
    └── README.md
```
## Modelo ML:
O modelo utilizado foi o Random Forest Classifier, foi testado alguns modelos mais robustos mas não obtive melhoras significativas.

Uma das maiores dificuldade foi o desbalanceamento entre as classes (poucos individuos foram de fato contratados) e a baixa qualidade dos dados (muitas informações faltantes). Devido a isso foi feito um sample dos dados para eliminar o desbalanceamento e a comparação entre colunas para a criação das features.

### Score do modelo
    precision    recall  f1-score   support

           0       0.50      0.40      0.45       217
           1       0.35      0.41      0.38       186
           2       0.37      0.40      0.38       197

    accuracy                           0.40       600
    macro avg      0.41      0.40      0.40       600
    weighted avg   0.41      0.40      0.40       600

### Features 
1. similaridade

    Compara o contexto da vaga (competencia_tecnicas_e_comportamentais e principais_atividades) com o curriculo do participante (cv_pt) e atruibui um score.
1. avaliador_idioma_ingles

    Compara o nível do idioma inglês necessário para a vaga e compara com a informação disponibilizada pelo candidato e atribui um score.
1. avaliador_idioma_espanhol

    Compara o nível do idioma espanhol necessário para a vaga e compara com a informação disponibilizada pelo candidato e atribui um score.

### Output
Baseado nas informações inseridas no Streamlit, o backend vai calcular os scores das features e enviar para a API, que usará o modelo para enviar a resposta de baixo, médio ou alto nível de conformidade candidato/vaga.

## Features

1. Fastapi: Foi utilizada para criar a api, onde carrega o modelo e aplica as predições com base nos valores da fetures incluidas nas chamadas.
1. Streamlit: Foi utilizado para criar um front-end no intuito de facilitar a inserção das informações pelo usuário final (pick list do nível de idioma e compo de texto para inserir informações sobre a vaga).
1. Prometheus: Utilizado para a observabilidade da saúde do modelo e da API.
1. Grafana: Dashboard que ingere informações do Prometheus e disponibiliza em uma UI amigável.

## Execução:
1. docker compose up --build
1. Fastapi: http://localhost:8000/
1. Streamlit: http://localhost:8501/
1. Prometheus: http://localhost:9090/
1. Grafana: http://localhost:3000/

Para a utilização do Grafana é necessário importar manualmente o arquivo do dashboard na interface web. Clique em +, import json, e import o arquivo grafana.json que está na pasta app_5.

## Melhorias Futuras

1. Adição de um banco de dados, atualmente as informações de log estão sendo gravados na memória volátil.
1. Criação e de requerimentos para cada conteiner a fim de diminuir o tamanho dos conteineres.
1. Aplicação do Docker Swarm para melhor escalabilidade e prevenção de falhas.
1. Aplicar outros tipos de modelos, mas principalmente trabalhar melhor na partre das features, talvez trazendo dados de outras fontes, melhorando as comparações e balanceamento das classes. 