import streamlit as st
import requests
import preprocess 

st.set_page_config(page_title="Classificação com Stacking", layout="wide")

st.title("📊 Classificação com Stacking - Entrada Manual")

# Lista de features esperadas (exemplo, substitua com as reais)
features = ['perfil_vaga_nivel_ingles','perfil_vaga_nivel_espanhol','perfil_vaga_principais_atividades','perfil_vaga_competencia_tecnicas_e_comportamentais',
             'formacao_e_idiomas_nivel_ingles','formacao_e_idiomas_nivel_espanhol','cv_pt']

# Criar campos de entrada para cada feature
input_data = {}
st.markdown("### Insira os valores das features.")
st.markdown("#### 🗣️ Idiomas (Perfil da Vaga)")
input_data['perfil_vaga_nivel_ingles'] = st.selectbox("Inglês (vaga):", ['Nenhum','Básico', 'Intermediário', 'Avançado', 'Fluente','Técnico'])
input_data['perfil_vaga_nivel_espanhol'] = st.selectbox("Espanhol (vaga):", ['Nenhum','Básico', 'Intermediário', 'Avançado', 'Fluente','Técnico'])

st.markdown("#### 📝 Informações da Vaga")
input_data['perfil_vaga_principais_atividades'] = st.text_input(f"{'perfil_vaga_principais_atividades'}", value="")
input_data['perfil_vaga_competencia_tecnicas_e_comportamentais'] = st.text_input(f"{'perfil_vaga_competencia_tecnicas_e_comportamentais'}", value="")

st.markdown("#### 🎓 Formação e Idiomas (Candidato)")
input_data['formacao_e_idiomas_nivel_ingles'] = st.selectbox("Inglês (candidato):", ['Nenhum','Básico', 'Intermediário', 'Avançado', 'Fluente','Técnico'])
input_data['formacao_e_idiomas_nivel_espanhol'] = st.selectbox("Espanhol (candidato):", ['Nenhum','Básico', 'Intermediário', 'Avançado', 'Fluente','Técnico'])

st.markdown("#### 📄 Currículo")
input_data['cv_pt'] = st.text_input(f"{'cv_pt'}", value="")

# Mapeamento de classe para rótulo
classe_labels = {0: "alto", 1: "baixo", 2: "medio"}

# Botao de envio de informacao
if st.button("🔍 Enviar para previsão"):
    try:
        # Preprocessar os dados
        input_data['perfil_vaga_nivel_ingles'] = preprocess.hierarquia_idioma(input_data['perfil_vaga_nivel_ingles'])
        input_data['perfil_vaga_nivel_espanhol'] = preprocess.hierarquia_idioma(input_data['perfil_vaga_nivel_espanhol'])
        input_data['formacao_e_idiomas_nivel_ingles'] = preprocess.hierarquia_idioma(input_data['formacao_e_idiomas_nivel_ingles'])
        input_data['formacao_e_idiomas_nivel_espanhol'] = preprocess.hierarquia_idioma(input_data['formacao_e_idiomas_nivel_espanhol'])

        input_data['similaridade_atividades'] = preprocess.calcular_similaridade_vaga_curriculo(input_data['perfil_vaga_principais_atividades'], input_data['cv_pt'])
        input_data['similaridade_competencias'] = preprocess.calcular_similaridade_vaga_curriculo(input_data['perfil_vaga_competencia_tecnicas_e_comportamentais'], input_data['cv_pt'])

        input_data['avaliador_idioma_ingles'] = preprocess.avaliador_idioma(input_data['formacao_e_idiomas_nivel_ingles'], input_data['perfil_vaga_nivel_ingles'])
        input_data['avaliador_idioma_espanhol'] = preprocess.avaliador_idioma(input_data['formacao_e_idiomas_nivel_espanhol'], input_data['perfil_vaga_nivel_espanhol'])

        input_data['similaridade'] = preprocess.similaridade(input_data['similaridade_atividades'], input_data['similaridade_competencias'])

        payload = {
            "data": [{
                "similaridade": input_data['similaridade'],
                "avaliador_idioma_ingles": input_data['avaliador_idioma_ingles'],
                "avaliador_idioma_espanhol": input_data['avaliador_idioma_espanhol']
            }]
}


        with st.spinner("Enviando para a API..."):
            response = requests.post("http://localhost:8000/predict", json=payload)

        if response.status_code == 200:
            st.success("✅ Previsão realizada com sucesso!")
            # Pegando a classe predita
            classe_predita = response.json()[0]['classe_predita']       
            # Mostrando a classe
            st.markdown(f"### 🎯 Correlação entre candidato e vaga: **{classe_labels.get(classe_predita, 'Desconhecida')}**")

        else:
            st.error(f"Erro na API: {response.status_code}")
            st.text(response.text)

    except ValueError:
        st.error("❌ Verifique se todos os campos numéricos estão preenchidos corretamente.")
    except Exception as e:
        st.error(f"Erro inesperado: {e}")
