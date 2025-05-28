from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os
from app.monitoring import monitor_drift
from app.logging_config import setup_logging
import logging

# Configuração de logging
setup_logging()
logger = logging.getLogger(__name__)

# Carregar modelo e dados de referência
model = joblib.load('app/model/modelo_stacking.pkl')
reference_data = pd.read_csv('reference_data.csv')

# Criação da API
app = FastAPI(title="API de Classificação com Stacking")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="app/static"), name="static")

# Periodicamente calcule o drift
current_data_buffer = pd.DataFrame()

# Classe de entrada genérica
class InputData(BaseModel):
    data: List[dict]

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

@app.middleware("http")
async def monitor_drift_middleware(request: Request, call_next):
    """Middleware para coletar dados das requisições"""
    response = await call_next(request)
    
    if request.url.path == "/predict" and request.method == "POST":
        try:
            # Obter os dados da requisição
            input_data = await request.json()
            df = pd.DataFrame(input_data['data'])
            
            # Adicionar ao buffer de dados atuais
            global current_data_buffer
            current_data_buffer = pd.concat([current_data_buffer, df], ignore_index=True)
            
            # Monitorar drift periodicamente (ex: a cada 10 requisições)
            if len(current_data_buffer) >= 10:
                monitor_drift(current_data_buffer, reference_data)
                current_data_buffer = pd.DataFrame()  # Resetar buffer
                
        except Exception as e:
            logger.error(f"Erro no monitoramento: {str(e)}")
    
    return response

@app.post("/predict")
def predict_json(input_data: InputData):
    try:
        # Converter lista de dicionários para DataFrame
        df = pd.DataFrame(input_data.data)

        # Verificação opcional: checar número de features esperadas
        expected_cols = model.best_estimator_.named_steps['scaler'].n_features_in_
        if df.shape[1] != expected_cols:
            raise HTTPException(
                status_code=400,
                detail=f"Esperado {expected_cols} colunas, mas recebeu {df.shape[1]}"
            )

        # Prever
        predictions = model.best_estimator_.predict(df)

        # Anexar predições ao DataFrame original
        df['classe_predita'] = predictions

        # Retornar como lista de dicionários
        return df.to_dict(orient='records')
    
    except Exception as e:
        logger.error(f"Erro na predição: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))