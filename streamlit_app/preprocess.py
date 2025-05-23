from sentence_transformers import SentenceTransformer, util
model = SentenceTransformer('all-MiniLM-L6-v2')
import pandas as pd

# Carrega modelo de comparação semântica
model = SentenceTransformer('all-MiniLM-L6-v2')

def calcular_similaridade_vaga_curriculo(texto_vaga, resumo_curriculo):
    if pd.isna(texto_vaga) or pd.isna(resumo_curriculo):
        return 0.0
    else:
        # Gera embeddings dos textos
        embedding_vaga = model.encode(texto_vaga, convert_to_tensor=True)
        embedding_curriculo = model.encode(resumo_curriculo, convert_to_tensor=True)

        # Calcula a similaridade de cosseno entre os vetores
        similaridade = util.cos_sim(embedding_vaga, embedding_curriculo)

        # Retorna valor como float
        return similaridade.item()
    
def hierarquia_idioma(text):
    mapa = {
        '': 0, 'Nenhum': 0, 'Básico': 1, 'Intermediário': 2,
        'Avançado': 3, 'Fluente': 4, 'Técnico': 5
    }
    return mapa.get(text, 0)

def avaliador_idioma(candidato, vaga):
    mapa = {
        0: 1, 1: 0.5, 2: 0.25, 3: 0.125, 4: 0.0625, 5: 0.03125
    }
    candidato = (candidato - vaga)
    return mapa.get(candidato, 0)

def similaridade(atividades, competencias):
    if atividades >= competencias:
        return atividades
    else: return competencias