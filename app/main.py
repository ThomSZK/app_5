from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib
from fastapi.responses import FileResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os
from prometheus_client import start_http_server, Counter, Histogram
import time
from app.monitoring import calculate_drift  # Função atualizada
from app.logging_config import setup_logging
import logging
from fastapi.exceptions import RequestValidationError

# ===== Configuração Prometheus =====
start_http_server(8001)  # Inicia servidor de métricas na porta 8001

# Métricas customizadas
REQUEST_COUNT = Counter(
    'http_requests_total',
    'Total de requisições HTTP',
    ['method', 'endpoint', 'http_status']
)

REQUEST_LATENCY = Histogram(
    'http_request_latency_seconds',
    'Latência das requisições',
    ['endpoint']
)

# ===== Configuração da Aplicação =====
setup_logging()
logger = logging.getLogger(__name__)

model = joblib.load('app/model/modelo_stacking.pkl')
reference_data = pd.read_csv('reference_data.csv')

app = FastAPI(title="API de Classificação com Stacking")
app.mount("/static", StaticFiles(directory="app/static"), name="static")

current_data_buffer = pd.DataFrame()

class InputData(BaseModel):
    data: List[dict]

# ===== Middleware de Métricas =====
@app.middleware("http")
async def monitor_requests(request: Request, call_next):
    start_time = time.time()
    endpoint = request.url.path
    
    try:
        response = await call_next(request)
        
        # Coleta de métricas
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=response.status_code
        ).inc()
        
        REQUEST_LATENCY.labels(
            endpoint=endpoint
        ).observe(time.time() - start_time)
        
        # Monitoramento de drift (mantido do seu código original)
        # if endpoint == "/predict" and request.method == "POST":
        #     input_data = await request.json()
        #     df = pd.DataFrame(input_data['data'])
            
        #     global current_data_buffer
        #     current_data_buffer = pd.concat([current_data_buffer, df], ignore_index=True)
            
        #     if len(current_data_buffer) >= 10:
        #         calculate_drift(current_data_buffer, reference_data)
        #         result = calculate_drift(current_data_buffer, reference_data)
        #         logger.info(f"Resultado do drift: {result}")
        #         current_data_buffer = pd.DataFrame()
        return response
        
    except Exception as e:
        REQUEST_COUNT.labels(
            method=request.method,
            endpoint=endpoint,
            http_status=500
        ).inc()
        raise

# ===== Endpoints =====
@app.get("/")
def read_index():
    return FileResponse("app/static/index.html")

@app.post("/predict")
async def predict_json(input_data: InputData):
    try:
        # Converter para DataFrame
        df = pd.DataFrame(input_data.data)
        
        # Verificação de features
        expected_cols = model.best_estimator_.named_steps['scaler'].n_features_in_
        if df.shape[1] != expected_cols:
            missing = expected_cols - df.shape[1]
            raise HTTPException(
                status_code=400,
                detail=f"Esperado {expected_cols} features. Faltam {missing} colunas."
            )

        # Validação adicional dos dados
        if df.isnull().values.any():
            raise HTTPException(
                status_code=400,
                detail="Dados contêm valores nulos/inválidos"
            )

        # Prever
        predictions = model.best_estimator_.predict(df)

        # Drift de dados
        global current_data_buffer
        current_data_buffer = pd.concat([current_data_buffer, df], ignore_index=True)
        if len(current_data_buffer) >= 10:
            result = calculate_drift(current_data_buffer, reference_data)
            logger.info(f"Resultado do drift: {result}")
            current_data_buffer = pd.DataFrame()

        return {"predictions": predictions.tolist()}
        
    except ValueError as e:
        logger.error(f"Erro de validação: {str(e)}")
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Erro interno: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Erro interno no processamento")
    
@app.get("/health")
async def health_check():
    """Endpoint de health check para monitoramento"""
    return {"status": "healthy", "version": "1.0.0"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    logger.error(f"Erro de validação: {exc.errors()}")
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

@app.exception_handler(Exception)
async def generic_exception_handler(request: Request, exc: Exception):
    logger.error("Erro não tratado", exc_info=True)
    return JSONResponse(
        status_code=500,
        content={"detail": "Erro interno do servidor"},
    )