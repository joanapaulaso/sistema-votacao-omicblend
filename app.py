import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import json
import os


# Função para carregar dados do arquivo JSON
def load_data():
    if os.path.exists("dados.json"):
        with open("dados.json", "r") as f:
            return json.load(f)
    return {"decisions": []}


# Função para salvar dados no arquivo JSON
def save_data(data):
    with open("dados.json", "w") as f:
        json.dump(data, f)


# Carrega os dados ao iniciar o aplicativo
data = load_data()

# Configuração inicial
if "decisions" not in st.session_state:
    st.session_state.decisions = data["decisions"]
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "current_user" not in st.session_state:
    st.session_state.current_user = None
if "current_page" not in st.session_state:
    st.session_state.current_page = "login"

# Senha única para todos os usuários (isso deve ser alterado para uma senha mais segura)
SENHA_UNICA = "senha123"


# Função para salvar decisões em CSV
def save_to_csv():
    df = pd.DataFrame(st.session_state.decisions)
    df.to_csv("decisoes.csv", index=False)


# Página de entrada
def entrada():
    st.title("Entrada no Sistema")
    nome = st.text_input("Nome")
    senha = st.text_input("Senha", type="password")
    if st.button("Entrar"):
        if senha == SENHA_UNICA:
            st.session_state.logged_in = True
            st.session_state.current_user = nome
            st.session_state.current_page = "home"
            st.rerun()
        else:
            st.error("Senha incorreta.")


# Página inicial
def home():
    st.title("Sistema de Tomada de Decisão")
    st.write(f"Bem-vindo, {st.session_state.current_user}!")

    col1, col2 = st.columns(2)

    with col1:
        if st.button("Criar Votação", use_container_width=True):
            st.session_state.current_page = "criar_votacao"
            st.rerun()

    with col2:
        if st.button("Votar", use_container_width=True):
            st.session_state.current_page = "listar_votacoes"
            st.rerun()


# Página para criar votação
def criar_votacao():
    st.title("Criar Nova Votação")
    titulo = st.text_input("Título")
    descricao = st.text_area("Descrição")
    documentos = st.text_input("Documentos (link externo)")
    data_limite = st.date_input("Data limite para Votação")

    if st.button("Criar"):
        nova_decisao = {
            "titulo": titulo,
            "descricao": descricao,
            "documentos": documentos,
            "data_limite": data_limite.strftime("%Y-%m-%d"),
            "criador": st.session_state.current_user,
            "votos": [],
        }
        st.session_state.decisions.append(nova_decisao)
        save_data({"decisions": st.session_state.decisions})
        save_to_csv()
        st.success("Votação criada com sucesso!")
        st.session_state.current_page = "home"
        st.rerun()

    if st.button("Voltar para a página inicial"):
        st.session_state.current_page = "home"
        st.rerun()


# Página para listar votações
def listar_votacoes():
    st.title("Votações Disponíveis")
    if st.session_state.decisions:
        for idx, decisao in enumerate(st.session_state.decisions):
            st.subheader(f"{idx + 1}. {decisao['titulo']}")
            st.write(f"Criado por: {decisao['criador']}")
            st.write(f"Data limite: {decisao['data_limite']}")
            if st.button(f"Votar na decisão {idx + 1}"):
                st.session_state.current_page = "votar"
                st.session_state.votacao_atual = idx
                st.rerun()
    else:
        st.write("Não há votações disponíveis no momento.")

    if st.button("Voltar para a página inicial"):
        st.session_state.current_page = "home"
        st.rerun()


# Função para criar gráfico de resultados
def criar_grafico_resultados(decisao):
    votos = decisao["votos"]
    contagem = {"De acordo": 0, "Não concordo": 0, "Indiferente": 0}
    for voto in votos:
        contagem[voto["voto"]] += 1

    fig = go.Figure(
        data=[
            go.Bar(
                x=list(contagem.keys()),
                y=list(contagem.values()),
                text=list(contagem.values()),
                textposition="auto",
            )
        ]
    )
    fig.update_layout(
        title_text="Resultados da Votação",
        xaxis_title="Opções",
        yaxis_title="Número de Votos",
    )
    return fig


# Página para votar
def votar():
    decisao = st.session_state.decisions[st.session_state.votacao_atual]
    st.title(f"Votar: {decisao['titulo']}")

    st.write(f"Descrição: {decisao['descricao']}")
    st.write(f"Documentos: {decisao['documentos']}")
    st.write(f"Data limite: {decisao['data_limite']}")

    voto = st.radio("Seu voto", ["De acordo", "Não concordo", "Indiferente"])
    justificativa = st.text_area(
        "Justificativa (obrigatória para 'Não concordo' e 'Indiferente')"
    )

    if st.button("Confirmar Voto"):
        if (voto in ["Não concordo", "Indiferente"]) and not justificativa:
            st.error("Justificativa obrigatória para 'Não concordo' e 'Indiferente'.")
        else:
            novo_voto = {
                "membro": st.session_state.current_user,
                "voto": voto,
                "justificativa": justificativa,
                "data_hora": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            }
            decisao["votos"].append(novo_voto)
            save_data({"decisions": st.session_state.decisions})
            save_to_csv()
            st.success("Voto registrado com sucesso!")

            # Exibir sumário parcial
            st.subheader("Sumário Parcial da Votação")
            votos_de_acordo = sum(
                1 for v in decisao["votos"] if v["voto"] == "De acordo"
            )
            votos_nao_concordo = sum(
                1 for v in decisao["votos"] if v["voto"] == "Não concordo"
            )
            votos_indiferente = sum(
                1 for v in decisao["votos"] if v["voto"] == "Indiferente"
            )

            st.write(f"De acordo: {votos_de_acordo}")
            st.write(f"Não concordo: {votos_nao_concordo}")
            st.write(f"Indiferente: {votos_indiferente}")

            # Exibir gráfico de resultados
            st.plotly_chart(criar_grafico_resultados(decisao))

    if st.button("Voltar para a lista de votações"):
        st.session_state.current_page = "listar_votacoes"
        st.rerun()


# Execução principal
if not st.session_state.logged_in:
    entrada()
else:
    if st.session_state.current_page == "home":
        home()
    elif st.session_state.current_page == "criar_votacao":
        criar_votacao()
    elif st.session_state.current_page == "listar_votacoes":
        listar_votacoes()
    elif st.session_state.current_page == "votar":
        votar()

# Botão para baixar CSV
if st.sidebar.button("Baixar Resultados (CSV)"):
    save_to_csv()
    st.sidebar.download_button(
        label="Clique para baixar",
        data=open("decisoes.csv", "rb").read(),
        file_name="decisoes.csv",
        mime="text/csv",
    )

# Botão de logout
if st.session_state.logged_in:
    if st.sidebar.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.current_user = None
        st.session_state.current_page = "login"
        st.rerun()
