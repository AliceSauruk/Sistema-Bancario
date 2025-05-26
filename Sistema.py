import textwrap
from datetime import datetime, date

def menu():
    """Exibe o menu de opções numérico para o usuário."""
    menu_texto = """
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo Usuário
    [5]\tNova Conta
    [6]\tListar Contas
    [7]\tSair
    => """
    return input(textwrap.dedent(menu_texto))

def depositar(saldo, valor, extrato, /):
    """Realiza a operação de depósito e retorna o novo saldo e extrato."""
    if valor > 0:
        saldo += valor
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        extrato += f"[{timestamp}] Depósito:\tR$ {valor:.2f}\n"
        print("\n=== Depósito realizado com sucesso! ===")
        return saldo, extrato, True
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
        return saldo, extrato, False

def sacar(*, saldo, valor, extrato, limite, numero_saques, limite_saques):
    """Realiza a operação de saque e retorna o novo estado da conta."""
    excedeu_saldo = valor > saldo
    excedeu_limite_valor = valor > limite
    excedeu_limite_saques = numero_saques >= limite_saques

    if excedeu_saldo:
        print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
    elif excedeu_limite_valor:
        print("\n@@@ Operação falhou! O valor do saque excede o limite. @@@")
    elif excedeu_limite_saques:
        print(f"\n@@@ Operação falhou! Número máximo de {limite_saques} saques diários foi atingido. @@@")
    elif valor > 0:
        saldo -= valor
        numero_saques += 1
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        extrato += f"[{timestamp}] Saque:\t\tR$ {valor:.2f}\n"
        print("\n=== Saque realizado com sucesso! ===")
        return saldo, extrato, numero_saques, True
    else:
        print("\n@@@ Operação falhou! O valor informado é inválido. @@@")
    
    return saldo, extrato, numero_saques, False

def exibir_extrato(saldo, /, *, extrato):
    """Exibe o extrato formatado da conta."""
    print("\n================ EXTRATO ================")
    print("Não foram realizadas movimentações." if not extrato else extrato)
    print(f"\nSaldo:\t\tR$ {saldo:.2f}")
    print("==========================================")

def criar_usuario(usuarios):
    """Cria um novo cliente (usuário) no sistema."""
    cpf = input("Informe o CPF (somente número): ")
    if any(u['cpf'] == cpf for u in usuarios):
        print("\n@@@ Já existe usuário com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")
    usuarios.append({"nome": nome, "data_nascimento": data_nascimento, "cpf": cpf, "endereco": endereco})
    print("\n=== Usuário criado com sucesso! ===")

def criar_conta_corrente(agencia, proximo_numero_conta, usuarios, contas):
    """Cria uma nova conta e a vincula a um usuário existente."""
    cpf = input("Informe o CPF do usuário para vincular a conta: ")
    usuario_encontrado = next((u for u in usuarios if u['cpf'] == cpf), None)

    if not usuario_encontrado:
        print("\n@@@ Usuário não encontrado! Crie o usuário antes de abrir uma conta. @@@")
        return

    nova_conta = {
        "agencia": agencia,
        "numero_conta": proximo_numero_conta,
        "usuario": usuario_encontrado,
        "saldo": 0.0,
        "extrato": "",
        "limite_valor_saque": 500.0,
        "limite_saques": 3,
        "numero_saques": 0,
        "limite_transacoes_diarias": 10,
        "transacoes_hoje": 0,
        "data_ultima_transacao": date.today()
    }
    contas.append(nova_conta)
    print(f"\n=== Conta Nº {proximo_numero_conta} criada com sucesso para {usuario_encontrado['nome']}! ===")

def listar_contas(contas):
    """Exibe os detalhes de todas as contas cadastradas."""
    if not contas:
        print("\nNenhuma conta cadastrada.")
        return
    for conta in contas:
        linha = f"""\
            Agência:\t{conta['agencia']}
            C/C:\t\t{conta['numero_conta']}
            Titular:\t{conta['usuario']['nome']}
        """
        print("=" * 30)
        print(textwrap.dedent(linha))

def verificar_e_resetar_limites_diarios(conta):
    """Verifica se o dia mudou e reseta os contadores da conta se necessário."""
    hoje = date.today()
    if conta["data_ultima_transacao"] != hoje:
        conta["numero_saques"] = 0
        conta["transacoes_hoje"] = 0
        conta["data_ultima_transacao"] = hoje
        print(f"\n--- Limites diários da conta {conta['numero_conta']} foram resetados. ---")

def main():
    """Função principal que executa o sistema bancário."""
    AGENCIA = "0001"
    usuarios = []
    contas = []

    while True:
        try:
            opcao = int(menu())
        except ValueError:
            print("\n@@@ Opção inválida! Por favor, digite um número. @@@")
            continue

        if opcao == 1: # Depositar
            try:
                num_conta = int(input("Informe o número da conta para depósito: "))
                conta_alvo = next((c for c in contas if c['numero_conta'] == num_conta), None)
                if not conta_alvo:
                    print("\n@@@ Conta não encontrada! @@@")
                    continue

                verificar_e_resetar_limites_diarios(conta_alvo)

                if conta_alvo["transacoes_hoje"] >= conta_alvo["limite_transacoes_diarias"]:
                    print(f"\n@@@ Limite de {conta_alvo['limite_transacoes_diarias']} transações diárias atingido para esta conta! @@@")
                    continue

                valor = float(input("Informe o valor do depósito: "))
                saldo, extrato, sucesso = depositar(conta_alvo['saldo'], valor, conta_alvo['extrato'])
                if sucesso:
                    conta_alvo['saldo'] = saldo
                    conta_alvo['extrato'] = extrato
                    conta_alvo['transacoes_hoje'] += 1
            except ValueError:
                print("\n@@@ Entrada inválida. Por favor, insira números. @@@")

        elif opcao == 2: # Sacar
            try:
                num_conta = int(input("Informe o número da conta para saque: "))
                conta_alvo = next((c for c in contas if c['numero_conta'] == num_conta), None)
                if not conta_alvo:
                    print("\n@@@ Conta não encontrada! @@@")
                    continue
                
                verificar_e_resetar_limites_diarios(conta_alvo)

                if conta_alvo["transacoes_hoje"] >= conta_alvo["limite_transacoes_diarias"]:
                    print(f"\n@@@ Limite de {conta_alvo['limite_transacoes_diarias']} transações diárias atingido para esta conta! @@@")
                    continue

                valor = float(input("Informe o valor do saque: "))
                saldo, extrato, num_saques, sucesso = sacar(
                    saldo=conta_alvo['saldo'], valor=valor, extrato=conta_alvo['extrato'],
                    limite=conta_alvo['limite_valor_saque'], numero_saques=conta_alvo['numero_saques'],
                    limite_saques=conta_alvo['limite_saques']
                )
                if sucesso:
                    conta_alvo['saldo'], conta_alvo['extrato'], conta_alvo['numero_saques'] = saldo, extrato, num_saques
                    conta_alvo['transacoes_hoje'] += 1
            except ValueError:
                print("\n@@@ Entrada inválida. Por favor, insira números. @@@")

        elif opcao == 3: # Extrato
            try:
                num_conta = int(input("Informe o número da conta para extrato: "))
                conta_alvo = next((c for c in contas if c['numero_conta'] == num_conta), None)
                if conta_alvo:
                    exibir_extrato(conta_alvo['saldo'], extrato=conta_alvo['extrato'])
                else:
                    print("\n@@@ Conta não encontrada! @@@")
            except ValueError:
                print("\n@@@ Entrada inválida. Por favor, insira um número. @@@")

        elif opcao == 4: # Novo Usuário
            criar_usuario(usuarios)

        elif opcao == 5: # Nova Conta
            proximo_numero_conta = len(contas) + 1
            criar_conta_corrente(AGENCIA, proximo_numero_conta, usuarios, contas)

        elif opcao == 6: # Listar Contas
            listar_contas(contas)

        elif opcao == 7: # Sair
            print("\nSaindo do sistema... Obrigado por usar nosso banco!")
            break

        else:
            print("Operação inválida, por favor selecione novamente a operação desejada.")

# Executa o programinha
main()