import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Gestão Logística Catalent", layout="wide")

# Estilo "Branco"
st.markdown("""
    <style>
    .main { background-color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

# Cabeçalho com Logo
col1, col2 = st.columns([1, 4])
if os.path.exists("logo.png"):
    col1.image("logo.png", width=150)
col2.title("Gerenciador Logístico - Catalent")

ARQUIVO = "AgendamentoCatalent.xlsx"

# Carregar dados
if os.path.exists(ARQUIVO):
    df = pd.read_excel(ARQUIVO)
else:
    df = pd.DataFrame(columns=["Data", "Nome do Fornecedor", "Ordem de Compra", "Produto", "Qtd PALLETS", "Qtd Produto", "Nota Fiscal"])

# Sidebar para adição
with st.sidebar:
    st.header("Adicionar Registro")
    with st.form("form_registro"):
        data = st.date_input("Data")
        fornecedor = st.text_input("Fornecedor")
        oc = st.text_input("Ordem de Compra")
        produto = st.text_input("Produto")
        pallets = st.number_input("Qtd PALLETS", min_value=1)
        qtd = st.text_input("Qtd Produto")
        nf = st.text_input("Nota Fiscal")
        
        btn = st.form_submit_button("Salvar")
        
        if btn:
            total_dia = df[df['Data'] == str(data)]['Qtd PALLETS'].sum()
            if total_dia + pallets > 40:
                st.error(f"Limite excedido! Restam apenas {40 - total_dia} pallets.")
            else:
                novo = pd.DataFrame([[str(data), fornecedor, oc, produto, pallets, qtd, nf]], columns=df.columns)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_excel(ARQUIVO, index=False)
                st.success("Agendado!")
                st.rerun()

# Exibição Geral
st.subheader("Visão Geral")
st.dataframe(df, use_container_width=True)

# Painel Catalent (Senha) - Corrigido e Único
with st.expander("Acesso Exclusivo Catalent"):
    senha = st.text_input("Senha", type="password", key="senha_catalent")

    if senha == "Catalent2026":
        st.write("### 📊 Gráfico de Pallets")
        st.bar_chart(df.groupby('Data')['Qtd PALLETS'].sum())
        
        # --- EXCLUSÃO DE AGENDAMENTO ---
        st.subheader("🗑️ Excluir Agendamento")
        
        if not df.empty:
            linha_para_deletar = st.number_input(
                "Digite o ID da linha para excluir:", 
                min_value=0, 
                max_value=len(df) - 1, 
                value=0, 
                step=1
            )
            
            if st.button("Confirmar Exclusão"):
                df = df.drop(df.index[linha_para_deletar])
                df.to_excel(ARQUIVO, index=False)
                st.warning(f"Linha {linha_para_deletar} removida com sucesso!")
                st.rerun()
        else:
            st.info("Não há agendamentos para excluir.")
            
    elif senha != "":
        st.error("Senha incorreta!")