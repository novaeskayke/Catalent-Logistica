import streamlit as st
import pandas as pd
import os
import re

# Configuração da página
st.set_page_config(page_title="Agenda Catalent", layout="wide")
ARQUIVO = "AgendamentoCatalent.xlsx"
colunas = ["Data", "CNPJ", "Nome do Fornecedor", "Ordem de Compra", "Código do Produto", "Produto", "Qtd PALLETS", "Qtd Produto", "Nota Fiscal"]

# Carregar dados
if os.path.exists(ARQUIVO):
    df = pd.read_excel(ARQUIVO)
else:
    df = pd.DataFrame(columns=colunas)

# --- FUNÇÕES DE VALIDAÇÃO ---
def validar_cnpj(cnpj):
    return cnpj.isdigit() and len(cnpj) == 14

def validar_nf(nf):
    return nf.isdigit()

def validar_oc(oc):
    # Aceita formato "CLIENTE/NUMERO" ou apenas números
    return bool(re.match(r'^[a-zA-Z]+/\d+$|^\d+$', oc))

# --- SISTEMA DE ACESSO ---
st.sidebar.title("Acesso ao Sistema")
with st.sidebar.expander("Modo Catalent (Admin)"):
    senha = st.text_input("Senha Admin:", type="password")
    is_admin = (senha == "Catalent2026")

# LÓGICA PRINCIPAL
if is_admin:
    st.title("Painel Administrativo Catalent")
    st.dataframe(df, use_container_width=True)
    
    # Exclusão Global para Admin
    id_excluir = st.number_input("ID do agendamento para excluir:", min_value=0, max_value=len(df)-1 if not df.empty else 0)
    if st.button("EXCLUIR REGISTRO (ADMIN)"):
        df = df.drop(index=id_excluir)
        df.to_excel(ARQUIVO, index=False)
        st.success("Registro removido com sucesso!")
        st.rerun()

else:
    tipo_acesso = st.sidebar.radio("Selecione:", ["Já possuo cadastro (Login)", "Primeiro Acesso/Novo Cadastro"])

    if tipo_acesso == "Já possuo cadastro (Login)":
        cnpj_login = st.sidebar.text_input("Digite seu CNPJ (apenas números):")
        if cnpj_login:
            df_fornecedor = df[df['CNPJ'].astype(str) == cnpj_login]
            st.title(f"Agenda Catalent - Fornecedor: {cnpj_login}")
            st.dataframe(df_fornecedor)
            
            if not df_fornecedor.empty:
                id_excluir = st.selectbox("Selecione o agendamento para excluir:", df_fornecedor.index)
                if st.button("Confirmar Exclusão"):
                    df = df.drop(index=id_excluir)
                    df.to_excel(ARQUIVO, index=False)
                    st.rerun()

    else:
        st.title("Primeiro Acesso / Novo Agendamento")
        with st.form("form_novo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            cnpj_input = col1.text_input("CNPJ (14 números)")
            fornecedor = col2.text_input("Nome do Fornecedor")
            data = st.date_input("Data")
            oc = st.text_input("Ordem de Compra (Ex: Cliente/123 ou 123)")
            cod_prod = st.text_input("Código do Produto")
            prod = st.text_input("Produto")
            pallets = st.number_input("Qtd PALLETS", min_value=1, step=1)
            
            qtd_num = st.number_input("Quantidade", min_value=1)
            unidade = st.text_input("Unidade de Medida (ou deixe vazio para 'Kit')")
            nf = st.text_input("Nota Fiscal (apenas números)")
            
            if st.form_submit_button("Cadastrar e Agendar"):
                # Validações de Formato
                if not validar_cnpj(cnpj_input): st.error("CNPJ inválido! Digite 14 números."); st.stop()
                if not validar_nf(nf): st.error("Nota Fiscal deve conter apenas números."); st.stop()
                if not validar_oc(oc): st.error("OC inválida! Use formato Cliente/Número ou apenas números."); st.stop()
                
                # --- REGRAS DE NEGÓCIO ---
                data_str = str(data)
                df_dia = df[df['Data'].astype(str) == data_str]
                
                # Trava de 4 entregas por dia
                if len(df_dia) >= 4:
                    st.error("Limite de 4 entregas atingido para este dia. Escolha outra data."); st.stop()
                
                # Trava de 30 pallets por dia
                if df_dia['Qtd PALLETS'].sum() + pallets > 30:
                    st.error(f"Limite de 30 pallets excedido! Restam apenas {30 - df_dia['Qtd PALLETS'].sum()} pallets."); st.stop()

                # Processamento e salvamento
                unidade_final = unidade if unidade.strip() != "" else "Kit"
                qtd_final = f"{qtd_num} {unidade_final}"
                
                novo = pd.DataFrame([[data_str, cnpj_input, fornecedor, oc, cod_prod, prod, pallets, qtd_final, nf]], columns=colunas)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_excel(ARQUIVO, index=False)
                st.success("Agendamento realizado com sucesso!")
                st.rerun()