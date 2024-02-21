# Importando bibliotecas

import streamlit as st
import pandas as pd
import numpy as np
import pydeck as pdk

from datetime import time
from plotly import express as px

# Configurando layout, nome e ícone da página

st.set_page_config(layout = "wide", page_title = "Análise de Acidentes em Rodovias", page_icon = "🛣️", )

# Carregando dados

@st.cache_data
def load_data():

    df = pd.read_excel('./BD-PRF-SUDESTE.xlsx')

    # Convertendo dados da coluna data em formato de data

    df['data'] = pd.to_datetime(df['data'], dayfirst= True)

    # Removendo horário vazio (00:00:00) da coluna data

    df['data'] = df['data'].dt.date

    # Criando nova coluna com data e horário

    df['data_completa'] = pd.to_datetime(df['data'].astype(str) + ' ' + df['hora'].astype(str))

    # Ordenando dados por data

    df = df.sort_values('data_completa')

    # Convertendo dados da coluna hora em formato de tempo

    df['hora'] = df['data_completa'].dt.time

    # Criando coluna com dia de semana do ocorrido

    df['dia_de_semana'] = df['data_completa'].dt.dayofweek

    return df


df = load_data()

st.toast("Dados carregados com sucesso !")

# Criando cópia

periodo = df.copy()

# Definindo data máxima e mínima da base de dados

min_data = df['data'].min()
max_data = df['data'].max()

# Criando colunas para organização

top_left, top_right = st.columns([2, 1])
col_left, col_center, col_right = st.columns([1, 2, 1])

# Título da página

top_left.markdown(" # Análise de Acidentes em Rodovias ")
top_left.markdown(" ### Estudo feito com base em registros de acidentes em rodovias federais nos anos de 2018, 2019 e 2020")

# Criando seletor de datas para o período a ser analisado

data_inicial = st.sidebar.date_input("Selecione a data inicial:",
                                     value = min_data,
                                     min_value = min_data,
                                     max_value = max_data,
                                     format = "DD/MM/YYYY")

data_final = st.sidebar.date_input("Selecione a data final:",
                                   value = max_data,
                                   min_value = min_data,
                                   max_value = max_data,
                                   format = "DD/MM/YYYY")

# Filtrando dados a partir da data selecionada pelo usuário
periodo = periodo[(periodo['data'] >= data_inicial) & (periodo['data'] <= data_final)]

st.sidebar.markdown("<br><br><br>", unsafe_allow_html = True)

# Criando slider para selecionar período de horário

hora_selecionada = st.sidebar.slider("Selecione o horário:",
                                     value = (time(0, 0), time(23,59)))

# Filtrando dados a partir do horário selecionado pelo usuário

periodo = periodo[(periodo['data_completa'].dt.time >= hora_selecionada[0]) & (periodo['data_completa'].dt.time <= hora_selecionada[1])]

st.sidebar.markdown("<br><br><br>", unsafe_allow_html = True)

# Exibindo contador de registros (atualizado de acordo com período selecionado)

st.sidebar.write("<h1 style='text-align:center;'>Número de acidentes registrados no período:</h1>", unsafe_allow_html = True)
contador = str(periodo.shape[0])
st.sidebar.markdown(f"<h1 style='color:white;text-align:center;'>{contador}</h1>", unsafe_allow_html = True)

# Adicionando uma função para enviar arquivos

foto_enviada = top_right.file_uploader("Presenciou um acidente ? Envie o seu registro: ")
if foto_enviada:
    top_right.success(f"{foto_enviada.name} enviado com sucesso !")

# Criando e plotando gráfico de barras exibindo contagem de registros por fase do dia

reg_fase_dia = px.histogram(periodo, x='fase_dia', histfunc=  'count',
                            labels = {'fase_dia': ''})

reg_fase_dia.update_layout(height = 550)

col_right.markdown("<h5 style='text-align: center;'>Acontecimentos por fase do dia</h5>", unsafe_allow_html = True)
col_right.plotly_chart(reg_fase_dia,
                       use_container_width = True)

# Criando mapa 

@st.cache_data
def load_map():
    map_data = periodo[['latitude', 'longitude']].to_dict(orient = 'records')
    layer = pdk.Layer(
        'ScatterplotLayer',
        data=map_data,
        get_position='[longitude, latitude]',
        get_radius = 500,
        get_fill_color = [131, 201, 255],
        pickable = True
    )
    layer_dict = layer
    view_state = pdk.ViewState(latitude = -19.9198, longitude = -43.9290, zoom = 5)
    mapa = pdk.Deck(layers = [layer_dict], initial_view_state = view_state)
    return mapa

col_center.markdown("<h5 style='text-align: center;'>Mapa dos Acidentes</h5>", unsafe_allow_html = True)
col_center.pydeck_chart(load_map())

# Criando e plotando gráfico de pie exibindo contagem de causas dos acidentes

col_left.markdown("<h5 style='text-align: center;'>Causas dos Acidentes</h5>", unsafe_allow_html = True)

contagem_causas = periodo['causa_acidente'].value_counts().reset_index()
contagem_causas.columns = ['Causa', 'Contagem']
contagem_causas = contagem_causas.sort_values('Contagem', ascending = False)[:7]

reg_causa_acidente = px.pie(contagem_causas, 
                            values= 'Contagem',
                            names = 'Causa')

reg_causa_acidente.update_layout(height = 550,
                                 width = 300,
                                 showlegend = False)

col_left.plotly_chart(reg_causa_acidente)
