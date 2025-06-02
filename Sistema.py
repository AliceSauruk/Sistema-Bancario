import textwrap
from datetime import datetime, date
from abc import ABC, abstractmethod

class Transacao(ABC):
    """Classe abstrata para representar uma transação bancária."""
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    @abstractmethod
    def registrar(self, conta):
        """Registra a transação na conta e no histórico."""
        pass

    def __str__(self):
        # Para facilitar a exibição no extrato
        timestamp = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        tipo_transacao = self.__class__.__name__
        return f"[{timestamp}] {tipo_transacao}:\t\tR$ {self.valor:.2f}"

class Deposito(Transacao):
    """Representa uma transação de depósito."""
    def registrar(self, conta):
        if self.valor > 0:
            conta._saldo += self.valor
            conta.historico.adicionar_transacao(self)
            return True
        return False

class Saque(Transacao):
    """Representa uma transação de saque."""
    def registrar(self, conta):
        # A lógica de validação do saque (limites, saldo)
        # é feita na classe ContaCorrente antes de criar o objeto Saque.
        # Aqui, apenas registramos se o saque é válido em termos de valor.
        if self.valor > 0 and self.valor <= conta.saldo: # Garantia extra
            conta._saldo -= self.valor
            conta.historico.adicionar_transacao(self)
            # A contagem de saques diários é feita na ContaCorrente
            return True
        return False

class Historico:
    """Gerencia o histórico de transações de uma conta."""
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao: Transacao):
        self._transacoes.append(transacao)

    def gerar_extrato(self):
        extrato_str = ""
        if not self._transacoes:
            return "Não foram realizadas movimentações."
        for transacao_obj in self._transacoes: # Renomeado para evitar conflito com transacao no loop abaixo
            extrato_str += str(transacao_obj) + "\n" # Usa o __str__ da Transacao
        return extrato_str

class Cliente:
    """Classe base para clientes do banco."""
    def __init__(self, endereco: str):
        self.endereco = endereco
        self.contas = [] # Lista de objetos Conta

    def adicionar_conta(self, conta):
        self.contas.append(conta)

class PessoaFisica(Cliente):
    """Representa um cliente pessoa física."""
    def __init__(self, nome: str, data_nascimento: str, cpf: str, endereco: str):
        super().__init__(endereco)
        self.nome = nome
        try:
            # Tenta converter a data, mas não impede a criação do objeto se falhar
            self.data_nascimento_obj = datetime.strptime(data_nascimento, "%d-%m-%Y").date()
            self.data_nascimento_str = data_nascimento
        except ValueError:
            self.data_nascimento_obj = None # Ou alguma outra forma de indicar data inválida
            self.data_nascimento_str = data_nascimento # Mantém a string original
            print(f"@@@ Data de nascimento '{data_nascimento}' em formato inválido. Use dd-mm-aaaa. Armazenada como string. @@@")
        self.cpf = cpf

    def __str__(self):
        return f"Cliente: {self.nome} (CPF: {self.cpf})"


class Conta:
    """Classe base para contas bancárias."""
    AGENCIA_PADRAO = "0001"

    def __init__(self, numero: int, cliente: PessoaFisica): # Cliente agora é PessoaFisica
        self._saldo = 0.0
        self._numero = numero
        self._agencia = Conta.AGENCIA_PADRAO
        self._cliente = cliente # Espera um objeto PessoaFisica
        self._historico = Historico()

    @property
    def saldo(self):
        return self._saldo

    @property
    def numero(self):
        return self._numero

    @property
    def agencia(self):
        return self._agencia

    @property
    def cliente(self) -> PessoaFisica: # Tipo anotado para clareza
        return self._cliente

    @property
    def historico(self) -> Historico: # Tipo anotado para clareza
        return self._historico

    @classmethod
    def nova_conta(cls, cliente: PessoaFisica, numero: int):
        return cls(numero, cliente)

    def depositar(self, valor: float) -> bool:
        """Realiza um depósito na conta."""
        if valor <= 0:
            print("\n@@@ Operação falhou! O valor do depósito deve ser positivo. @@@")
            return False
        deposito = Deposito(valor)
        sucesso = deposito.registrar(self)
        if sucesso:
            print("\n=== Depósito realizado com sucesso! ===")
        else:
            print("\n@@@ Operação falhou! Não foi possível registrar o depósito. @@@")
        return sucesso

    @abstractmethod
    def sacar(self, valor: float) -> bool:
        """Método abstrato para saque (será implementado em classes filhas)."""
        pass

class ContaCorrente(Conta):
    """Representa uma conta corrente, com limites específicos."""
    def __init__(self, numero: int, cliente: PessoaFisica, limite_valor_saque=500.0, limite_saques_diarios=3):
        super().__init__(numero, cliente)
        self._limite_valor_saque = limite_valor_saque
        self._limite_saques_diarios = limite_saques_diarios # Limite de 3 saques
        self._numero_saques_hoje = 0
        self._limite_transacoes_diarias = 10 # Limite de 10 transações gerais
        self._transacoes_hoje = 0
        self._data_ultima_transacao = date.min

    def _verificar_e_resetar_limites_diarios(self):
        hoje = date.today()
        if self._data_ultima_transacao != hoje:
            self._numero_saques_hoje = 0
            self._transacoes_hoje = 0
            self._data_ultima_transacao = hoje
            # print(f"\n--- Limites diários da conta {self.numero} foram resetados para {hoje}. ---") # Opcional

    def sacar(self, valor: float) -> bool:
        self._verificar_e_resetar_limites_diarios()

        if self._transacoes_hoje >= self._limite_transacoes_diarias:
            print(f"\n@@@ Limite de {self._limite_transacoes_diarias} transações gerais diárias atingido para esta conta! @@@")
            return False

        excedeu_saldo = valor > self.saldo
        excedeu_limite_valor = valor > self._limite_valor_saque
        excedeu_limite_saques = self._numero_saques_hoje >= self._limite_saques_diarios

        if valor <= 0:
            print("\n@@@ Operação falhou! O valor do saque deve ser positivo. @@@")
            return False
        if excedeu_saldo:
            print("\n@@@ Operação falhou! Você não tem saldo suficiente. @@@")
            return False
        if excedeu_limite_valor:
            print(f"\n@@@ Operação falhou! O valor do saque (R$ {valor:.2f}) excede o limite de R$ {self._limite_valor_saque:.2f}. @@@")
            return False
        if excedeu_limite_saques:
            print(f"\n@@@ Operação falhou! Número máximo de {self._limite_saques_diarios} saques diários ({self._numero_saques_hoje} já realizados) foi atingido. @@@")
            return False

        saque = Saque(valor)
        sucesso_registro = saque.registrar(self)

        if sucesso_registro:
            self._numero_saques_hoje += 1
            self._transacoes_hoje += 1
            print("\n=== Saque realizado com sucesso! ===")
            return True
        else:
            print("\n@@@ Operação falhou! Não foi possível registrar o saque. @@@")
            return False

    def depositar(self, valor: float) -> bool:
        self._verificar_e_resetar_limites_diarios()

        if self._transacoes_hoje >= self._limite_transacoes_diarias:
            print(f"\n@@@ Limite de {self._limite_transacoes_diarias} transações gerais diárias atingido para esta conta! @@@")
            return False

        sucesso = super().depositar(valor)
        if sucesso:
            self._transacoes_hoje += 1
        return sucesso


# ==============================================================================
# FUNÇÕES AUXILIARES DO SISTEMA (MENU E INTERAÇÃO COM USUÁRIO)
# ==============================================================================

def menu():
    menu_texto = """
    ================ MENU ================
    [1]\tDepositar
    [2]\tSacar
    [3]\tExtrato
    [4]\tNovo Usuário (Cliente)
    [5]\tNova Conta
    [6]\tListar Contas
    [7]\tSair
    => """
    return input(textwrap.dedent(menu_texto))

def filtrar_cliente_por_cpf(cpf, clientes_cadastrados):
    clientes_encontrados = [cliente for cliente in clientes_cadastrados if cliente.cpf == cpf]
    return clientes_encontrados[0] if clientes_encontrados else None

def recuperar_conta_cliente(numero_conta_input, contas_cadastradas):
    try:
        num_conta = int(numero_conta_input)
        conta_alvo = next((c for c in contas_cadastradas if c.numero == num_conta), None)
        return conta_alvo
    except ValueError:
        return None


def operacao_deposito(contas_cadastradas):
    num_conta_str = input("Informe o número da conta para depósito: ")
    conta_alvo = recuperar_conta_cliente(num_conta_str, contas_cadastradas)

    if not conta_alvo:
        print("\n@@@ Conta não encontrada! @@@")
        return

    try:
        valor = float(input("Informe o valor do depósito: "))
        conta_alvo.depositar(valor)
    except ValueError:
        print("\n@@@ Valor inválido. Por favor, insira um número. @@@")

def operacao_saque(contas_cadastradas):
    num_conta_str = input("Informe o número da conta para saque: ")
    conta_alvo = recuperar_conta_cliente(num_conta_str, contas_cadastradas)

    if not conta_alvo:
        print("\n@@@ Conta não encontrada! @@@")
        return

    try:
        valor = float(input("Informe o valor do saque: "))
        conta_alvo.sacar(valor)
    except ValueError:
        print("\n@@@ Valor inválido. Por favor, insira um número. @@@")

def operacao_extrato(contas_cadastradas):
    num_conta_str = input("Informe o número da conta para extrato: ")
    conta_alvo = recuperar_conta_cliente(num_conta_str, contas_cadastradas)

    if not conta_alvo:
        print("\n@@@ Conta não encontrada! @@@")
        return

    print("\n================ EXTRATO ================")
    print(conta_alvo.historico.gerar_extrato())
    print(f"Saldo:\t\tR$ {conta_alvo.saldo:.2f}")
    print("==========================================")


def operacao_novo_cliente(clientes_cadastrados):
    cpf = input("Informe o CPF (somente número): ")
    cliente_existente = filtrar_cliente_por_cpf(cpf, clientes_cadastrados)
    if cliente_existente:
        print("\n@@@ Já existe cliente com esse CPF! @@@")
        return

    nome = input("Informe o nome completo: ")
    data_nascimento = input("Informe a data de nascimento (dd-mm-aaaa): ")
    endereco = input("Informe o endereço (logradouro, nro - bairro - cidade/sigla estado): ")

    novo_cliente = PessoaFisica(nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes_cadastrados.append(novo_cliente)
    print(f"\n=== Cliente {novo_cliente.nome} criado com sucesso! ===")

def operacao_nova_conta(proximo_numero_conta, clientes_cadastrados, contas_cadastradas):
    cpf_cliente = input("Informe o CPF do cliente para vincular a conta: ")
    cliente_titular = filtrar_cliente_por_cpf(cpf_cliente, clientes_cadastrados)

    if not cliente_titular:
        print("\n@@@ Cliente não encontrado! Crie o cliente antes de abrir uma conta. @@@")
        return None # Retorna None para indicar que a conta não foi criada

    nova_conta = ContaCorrente(numero=proximo_numero_conta, cliente=cliente_titular)
    contas_cadastradas.append(nova_conta)
    cliente_titular.adicionar_conta(nova_conta)

    print(f"\n=== Conta Nº {nova_conta.numero} (Ag: {nova_conta.agencia}) criada com sucesso para {cliente_titular.nome}! ===")
    return proximo_numero_conta + 1

def operacao_listar_contas(contas_cadastradas):
    if not contas_cadastradas:
        print("\nNenhuma conta cadastrada.")
        return
    for conta in contas_cadastradas:
        linha = f"""\
            Agência:\t{conta.agencia}
            C/C:\t\t{conta.numero}
            Titular:\t{conta.cliente.nome} (CPF: {conta.cliente.cpf})
            Saldo:\t\tR$ {conta.saldo:.2f}
        """
        print("=" * 40)
        print(textwrap.dedent(linha))

# ==============================================================================
# FUNÇÃO PRINCIPAL (MAIN LOOP)
# ==============================================================================

def main():
    clientes_cadastrados = []
    contas_cadastradas = []
    proximo_numero_conta_global = 1

    while True:
        try:
            opcao_menu = int(menu())
        except ValueError:
            print("\n@@@ Opção inválida! Por favor, digite um número. @@@")
            continue

        if opcao_menu == 1:
            operacao_deposito(contas_cadastradas)
        elif opcao_menu == 2:
            operacao_saque(contas_cadastradas)
        elif opcao_menu == 3:
            operacao_extrato(contas_cadastradas)
        elif opcao_menu == 4:
            operacao_novo_cliente(clientes_cadastrados)
        elif opcao_menu == 5:
            resultado_num_conta = operacao_nova_conta(proximo_numero_conta_global, clientes_cadastrados, contas_cadastradas)
            if resultado_num_conta is not None: # Verifica se a conta foi criada
                proximo_numero_conta_global = resultado_num_conta
        elif opcao_menu == 6:
            operacao_listar_contas(contas_cadastradas)
        elif opcao_menu == 7:
            print("\nSaindo do sistema... Obrigado por usar nosso banco!")
            break
        else:
            print("\n@@@ Operação inválida, por favor selecione novamente a operação desejada. @@@")

# Inicia o programinha
if __name__ == "__main__":
    main()