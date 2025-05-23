from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
import joblib
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

# Carregar modelo treinado
model = joblib.load('model/modelo_stacking.pkl')

# Criação da API
app = FastAPI(title="API de Classificação com Stacking")

# Servir arquivos estáticos
app.mount("/static", StaticFiles(directory="static"), name="static")

# Classe de entrada genérica (usaremos dicionários em vez de campos fixos)
class InputData(BaseModel):
    data: List[dict]

@app.get("/")
def read_index():
    return FileResponse("static/index.html")

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
        raise HTTPException(status_code=500, detail=str(e))