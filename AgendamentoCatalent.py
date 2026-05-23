import pandas as pd
import os

# Nome do arquivo
ARQUIVO = "AgendamentoCatalent.xlsx"

def carregar_agenda():
    """Carrega a planilha se existir, ou cria uma nova estrutura."""
    colunas = [
        "Data", "Nome do Fornecedor", "Ordem de Compra", 
        "Produto", "Qtd PALLETS", "Qtd Produto", "Nota Fiscal"
    ]
    if os.path.exists(ARQUIVO):
        return pd.read_excel(ARQUIVO)
    else:
        return pd.DataFrame(columns=colunas)

def adicionar_registro(df):
    """Coleta os dados do usuário e verifica limite de PALLETS."""
    print("\n--- Preencha os dados abaixo ---")
    data = input("Data (DD/MM/AAAA): ")
    
    # --- Lógica de verificação de limite ---
    # Filtra os registros existentes apenas para a data informada
    if not df.empty:
        # Garante que a coluna de pallets seja tratada como número para soma
        df['Qtd PALLETS'] = pd.to_numeric(df['Qtd PALLETS'], errors='coerce').fillna(0)
        registros_dia = df[df['Data'] == data]
        total_atual = registros_dia['Qtd PALLETS'].sum()
    else:
        total_atual = 0
        
    print(f"Total de pallets já agendados para {data}: {total_atual}/40")
    
    try:
        pallets = int(input("Quantidade de PALLETS a adicionar: "))
    except ValueError:
        print("\n[ERRO] Digite um número válido para a quantidade de PALLETS.")
        return df

    if total_atual + pallets > 40:
        print(f"\n[ERRO] Limite excedido! Você já tem {total_atual} pallets e só pode adicionar mais {40 - total_atual}.")
        return df 
    # ---------------------------------------

    fornecedor = input("Nome do fornecedor: ")
    oc = input("Ordem de compra: ")
    produto = input("Produto: ")
    qtd_produto = input("Quantidade do produto: ")
    nf = input("Nota fiscal: ")
    
    novo_dado = {
        "Data": data,
        "Nome do Fornecedor": fornecedor,
        "Ordem de Compra": oc,
        "Produto": produto,
        "Qtd PALLETS": pallets,
        "Qtd Produto": qtd_produto,
        "Nota Fiscal": nf
    }
    
    nova_linha = pd.DataFrame([novo_dado])
    df = pd.concat([df, nova_linha], ignore_index=True)
    
    # Salva no arquivo
    df.to_excel(ARQUIVO, index=False)
    print("\n[OK] Registro adicionado e planilha salva!")
    return df

# Fluxo Principal
agenda = carregar_agenda()

while True:
    print("\n=== GERENCIADOR LOGÍSTICO CATALENT ===")
    print("1. Visualizar Planilha")
    print("2. Adicionar Registro")
    print("3. Sair")
    
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        if agenda.empty:
            print("\nA planilha está vazia.")
        else:
            print("\n", agenda.to_string())
    elif opcao == "2":
        agenda = adicionar_registro(agenda)
    elif opcao == "3":
        print("Saindo do sistema...")
        break
    else:
        print("Opção inválida, tente novamente.")

        import pandas as pd
import os

ARQUIVO = "AgendamentoCatalent.xlsx"

# ... (Mantenha as funções carregar_agenda e adicionar_registro iguais) ...

def painel_catalent(df):
    """Exibe um resumo consolidado para a Catalent."""
    print("\n=== PAINEL EXCLUSIVO: VISÃO CATALENT ===")
    if df.empty:
        print("Nenhum agendamento encontrado.")
        return

    # Garante que os valores são numéricos
    df['Qtd PALLETS'] = pd.to_numeric(df['Qtd PALLETS'], errors='coerce').fillna(0)
    
    # Agrupa por data e soma os pallets
    resumo = df.groupby('Data')['Qtd PALLETS'].sum().reset_index()
    
    print("\n--- Total de PALLETS por Dia ---")
    print(resumo.to_string(index=False))
    
    print("\n--- Lista Completa de Agendamentos ---")
    print(df.to_string())
    input("\nPressione ENTER para voltar ao menu...")

# Fluxo Principal atualizado
agenda = carregar_agenda()

while True:
    print("\n=== GERENCIADOR LOGÍSTICO ===")
    print("1. Adicionar Registro (Fornecedor)")
    print("2. Painel Catalent (Exclusivo)")
    print("3. Sair")
    
    opcao = input("Escolha uma opção: ")

    if opcao == "1":
        agenda = adicionar_registro(agenda)
    elif opcao == "2":
        # Aqui você pode adicionar uma simples trava de senha
        senha = input("Digite a senha de acesso: ")
        if senha == "Catalent2026": 
            painel_catalent(agenda)
        else:
            print("[ERRO] Acesso negado!")
    elif opcao == "3":
        break