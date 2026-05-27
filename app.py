import streamlit as st
import pandas as pd
import os

# Configuração da página
st.set_page_config(page_title="Agenda Catalent", layout="wide")
ARQUIVO = "AgendamentoCatalent.xlsx"
colunas = ["Data", "CNPJ", "Nome do Fornecedor", "Ordem de Compra", "Código do Produto", "Produto", "Qtd PALLETS", "Qtd Produto", "Nota Fiscal"]

# Carregar dados
if os.path.exists(ARQUIVO):
    df = pd.read_excel(ARQUIVO)
else:
    df = pd.DataFrame(columns=colunas)

# --- SISTEMA DE ACESSO ---
st.sidebar.title("Acesso ao Sistema")

# Bloco Admin Catalent
with st.sidebar.expander("Modo Catalent (Admin)"):
    senha = st.text_input("Senha de Acesso:", type="password")
    is_admin = (senha == "Catalent2026")

if is_admin:
    st.title("Painel Administrativo Catalent")
    st.write("Visualizando todos os agendamentos.")
    st.dataframe(df, use_container_width=True)
    st.info("Acesso Administrativo ativo.")

# Lógica Fornecedores
else:
    tipo_acesso = st.sidebar.radio("Selecione:", ["Já possuo cadastro (Login)", "Primeiro Acesso/Novo Cadastro"])

    if tipo_acesso == "Já possuo cadastro (Login)":
        cnpj_login = st.sidebar.text_input("Digite seu CNPJ:")
        if cnpj_login:
            if cnpj_login not in df['CNPJ'].astype(str).values:
                st.error("CNPJ não encontrado.")
            else:
                st.title(f"Agenda Catalent - Fornecedor: {cnpj_login}")
                df_fornecedor = df[df['CNPJ'].astype(str) == cnpj_login].copy()
                st.subheader("Meus Agendamentos")
                st.dataframe(df_fornecedor)
                if not df_fornecedor.empty:
                    id_excluir = st.selectbox("Selecione o agendamento para excluir:", df_fornecedor.index)
                    if st.button("Confirmar Exclusão"):
                        df = df.drop(index=id_excluir)
                        df.to_excel(ARQUIVO, index=False)
                        st.warning("Agendamento removido!")
                        st.rerun()

    else:
        st.title("Primeiro Acesso / Novo Agendamento")
        with st.form("form_novo_cadastro", clear_on_submit=True):
            col1, col2 = st.columns(2)
            cnpj_input = col1.text_input("CNPJ (Apenas números)")
            fornecedor = col2.text_input("Nome do Fornecedor")
            data = st.date_input("Data")
            oc = st.text_input("Ordem de Compra")
            cod_prod = st.text_input("Código do Produto")
            prod = st.text_input("Produto")
            pallets = st.number_input("Qtd PALLETS", min_value=1, step=1)
            qtd = st.text_input("Qtd Produto")
            nf = st.text_input("Nota Fiscal")
            
            if st.form_submit_button("Cadastrar e Agendar"):
                if not (cnpj_input and fornecedor and oc and cod_prod and prod and qtd and nf):
                    st.error("Todos os campos são obrigatórios!")
                else:
                    data_str = str(data)
                    df_dia = df[df['Data'].astype(str) == data_str]
                    if len(df_dia) >= 4:
                        st.error("Limite de 4 entregas atingido para este dia.")
                    elif df_dia['Qtd PALLETS'].sum() + pallets > 30:
                        st.error("Limite de 30 pallets excedido!")
                    else:
                        novo = pd.DataFrame([[data_str, cnpj_input, fornecedor, oc, cod_prod, prod, pallets, qtd, nf]], columns=colunas)
                        df = pd.concat([df, novo], ignore_index=True)
                        df.to_excel(ARQUIVO, index=False)
                        st.success("Agendamento realizado!")
                        st.rerun()