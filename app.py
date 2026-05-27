import streamlit as st
import pandas as pd
import os
import re
from datetime import date
from io import BytesIO

# Configuração da página
st.set_page_config(page_title="Agenda Catalent", layout="wide")
ARQUIVO = "AgendamentoCatalent.xlsx"
colunas = ["Data", "CNPJ", "Nome do Fornecedor", "Ordem de Compra", "Código do Produto", "Produto", "Qtd PALLETS", "Qtd Produto", "Nota Fiscal", "Status"]

# Inicializar estado da sessão para login
if "admin_logado" not in st.session_state:
    st.session_state.admin_logado = False

# Carregar dados
if os.path.exists(ARQUIVO):
    df = pd.read_excel(ARQUIVO)
    if "Status" not in df.columns: 
        df["Status"] = "Pendente"
        df.to_excel(ARQUIVO, index=False)
else:
    df = pd.DataFrame(columns=colunas)

# --- FUNÇÕES DE VALIDAÇÃO ---
def validar_cnpj(cnpj): return cnpj.isdigit() and len(cnpj) == 14
def validar_nf(nf): return nf.isdigit()
def validar_oc(oc): return bool(re.match(r'^[a-zA-Z]+/\d+$|^\d+$', oc))

# --- SISTEMA DE ACESSO ---
st.sidebar.title("Acesso ao Sistema")
with st.sidebar.expander("Modo Catalent (Admin)"):
    if not st.session_state.admin_logado:
        senha = st.text_input("Senha Admin:", type="password")
        if st.button("Entrar"):
            if senha == "Catalent2026":
                st.session_state.admin_logado = True
                st.rerun()
            else:
                st.error("Senha incorreta!")
    else:
        st.success("Administrador logado.")
        if st.button("Sair do Modo Admin"):
            st.session_state.admin_logado = False
            st.rerun()

# LÓGICA PRINCIPAL
if st.session_state.admin_logado:
    st.title("Painel Administrativo - Aprovação")
    
    st.divider()
    st.subheader(f"✅ Aprovados para hoje ({date.today()}):")
    df_hoje = df[(df['Data'].astype(str) == str(date.today())) & (df['Status'] == 'Aprovado')]
    st.dataframe(df_hoje, use_container_width=True)
    
    st.subheader("Todos os Agendamentos:")
    st.dataframe(df, use_container_width=True)
    
    output = BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False)
    st.download_button("📥 Baixar Planilha Geral", data=output.getvalue(), file_name="Relatorio_Agendamentos.xlsx", mime="application/vnd.ms-excel")
    
    st.divider()
    id_alvo = st.number_input("ID para alterar status/excluir:", min_value=0, max_value=len(df)-1 if not df.empty else 0)
    col_a1, col_a2 = st.columns(2)
    novo_status = col_a1.selectbox("Novo Status:", ["Pendente", "Aprovado", "Recusado"])
    
    if col_a1.button("Atualizar Status"):
        df.at[id_alvo, 'Status'] = novo_status
        df.to_excel(ARQUIVO, index=False)
        st.success(f"Status do ID {id_alvo} atualizado!"); st.rerun()
        
    if col_a2.button("EXCLUIR REGISTRO"):
        df = df.drop(index=id_alvo)
        df.to_excel(ARQUIVO, index=False)
        st.warning("Registro removido!"); st.rerun()

else:
    tipo_acesso = st.sidebar.radio("Selecione:", ["Consultar meus agendamentos", "Novo Agendamento"])

    if tipo_acesso == "Consultar meus agendamentos":
        cnpj_login = st.sidebar.text_input("Digite seu CNPJ (apenas números):")
        if cnpj_login:
            df_fornecedor = df[df['CNPJ'].astype(str) == cnpj_login]
            st.title(f"Meus Agendamentos - {cnpj_login}")
            st.dataframe(df_fornecedor)

    else:
        st.title("Solicitação de Agendamento")
        st.info("📌 **Instruções:** Preencha todos os campos. Após o envio, seu agendamento ficará como 'Pendente'.")
        
        with st.form("form_novo", clear_on_submit=True):
            col1, col2 = st.columns(2)
            cnpj_input = col1.text_input("CNPJ (14 números)")
            fornecedor = col2.text_input("Nome do Fornecedor")
            data = st.date_input("Data")
            oc = st.text_input("Ordem de Compra")
            cod_prod = st.text_input("Código do Produto")
            prod = st.text_input("Produto")
            pallets = st.number_input("Qtd PALLETS", min_value=1, step=1)
            qtd_num = st.number_input("Quantidade", min_value=1)
            unidade = st.text_input("Unidade (ou deixe vazio para 'Kit')")
            nf = st.text_input("Nota Fiscal")
            
            if st.form_submit_button("Solicitar Agendamento"):
                if not validar_cnpj(cnpj_input): st.error("CNPJ inválido!"); st.stop()
                if not validar_nf(nf): st.error("NF apenas números!"); st.stop()
                if not validar_oc(oc): st.error("OC inválida!"); st.stop()
                
                df_aprovados = df[df['Status'] == 'Aprovado']
                df_dia = df_aprovados[df_aprovados['Data'].astype(str) == str(data)]
                
                if len(df_dia) >= 4:
                    st.error("Limite de 4 agendamentos aprovados atingido."); st.stop()
                
                if df_dia['Qtd PALLETS'].sum() + pallets > 30:
                    st.error("Limite de 30 pallets excedido."); st.stop()

                unidade_final = unidade if unidade.strip() != "" else "Kit"
                novo = pd.DataFrame([[str(data), cnpj_input, fornecedor, oc, cod_prod, prod, pallets, 
                                     f"{qtd_num} {unidade_final}", nf, "Pendente"]], columns=colunas)
                df = pd.concat([df, novo], ignore_index=True)
                df.to_excel(ARQUIVO, index=False)
                st.success("Solicitação enviada!"); st.rerun()