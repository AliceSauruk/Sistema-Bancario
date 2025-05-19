def menu():
    print("===== MENU =====")
    print()
    print("1 - Depositar")
    print("2 - Sacar")
    print("3 - Extrato")
    print("4 - Sair")
    print()

def depositar(saldo, valor_deposito, extrato):
    while True:
        print()
        print("=== DEPÓSITO ===")
        print()
        valor_deposito = float(input("Informe o valor do depósito: R$ "))
        print()
        if valor_deposito > 0:
            saldo += valor_deposito
            extrato += f"Depósito: R$ {valor_deposito:.2f}\n"
            print(f"Depósito de R$ {valor_deposito:.2f} realizado com sucesso!")
            print(f"Seu saldo atual é: R$ {saldo:.2f}")
            print()
        elif valor_deposito <= 0:
            print()
            print("Valor inválido! O valor deve ser maior que zero.")
        if input("Deseja realizar outro depósito? (s/n): ").lower() == 'n':
            print("Operação encerrada.")
            print()
            break
    return saldo, extrato

def sacar(saldo, valor_saque, extrato, limite, numero_saques, limite_saques):
    while True:
        print()
        print("=== SAQUE ===")
        print()
        valor_saque = float(input("Informe o valor do saque: R$ "))
        print()
        if valor_saque < saldo and valor_saque < limite and numero_saques < limite_saques:
            saldo -= valor_saque
            extrato += f"Saque: R$ {valor_saque:.2f}\n"
            numero_saques += 1
            print(f"Saque de R$ {valor_saque:.2f} realizado com sucesso!")
            print(f"Seu saldo atual é: R$ {saldo:.2f}")
            print()
        elif valor_saque > saldo:
            print("Saldo insuficiente!")
        elif valor_saque > limite:
            print("Valor do saque excede o limite!")
        elif numero_saques >= limite_saques:
            print("Número máximo de saques atingido!")
        elif valor_saque <= 0:
            print("Valor inválido! O valor deve ser maior que zero.")
        if input("Deseja realizar outro saque? (s/n): ").lower() == 'n':
            print("Operação encerrada.")
            print()
            break
    return saldo, extrato, numero_saques

def extrair(saldo, extrato):
    print()
    print("=== EXTRATO ===")
    print()
    if not extrato:
        print("Não foram realizadas movimentações.")
    else:
        print(extrato)
    print(f"Saldo: R$ {saldo:.2f}")
    print()

saldo = 0
valor_deposito = 0
valor_saque = 0
extrato = ""
limite = 500
numero_saques = 0
limite_saques = 3

while True:
    menu()
    try:
        opcao = int(input("Escolha uma opção: "))
    except ValueError:
        print("Opção inválida! Tente novamente.")
        continue
    print

    if opcao not in [1, 2, 3, 4]:
        print("Opção inválida! Tente novamente.")
    if opcao == 1:
        saldo, extrato = depositar(saldo, valor_deposito, extrato)
    elif opcao == 2:
        saldo, extrato, numero_saques = sacar(saldo, valor_saque, extrato, limite, numero_saques, limite_saques)
    elif opcao == 3:
        extrair(saldo, extrato)
    elif opcao == 4:
        print("Saindo do sistema...")
        break