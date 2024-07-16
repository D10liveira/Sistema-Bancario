import random
import textwrap
from abc import ABC, abstractmethod
from datetime import datetime


class Cliente:
    def __init__(self, endereco):
        self.endereco = endereco
        self.contas = []

    def realizar_transacao(self, conta, transacao):
        transacao.registrar(conta)

    def adicionar_conta(self, conta):
        self.contas.append(conta)


class PessoaFisica(Cliente):
    def __init__(self, nome, data_nascimento, cpf, endereco):
        super().__init__(endereco)
        self.nome = nome
        self.data_nascimento = data_nascimento
        self.cpf = cpf


class Conta:
    def __init__(self, numero, cliente):
        self._saldo = 0
        self._numero = numero
        self._agencia = "0001"
        self._cliente = cliente
        self._extrato = Extrato()

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

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
    def cliente(self):
        return self._cliente

    @property
    def extrato(self):
        return self._extrato

    def sacar(self, valor):
        saldo = self.saldo
        excedeu_saldo = valor > saldo

        if excedeu_saldo:
            print("Você não possui saldo o suficiente.")
            cheque_especial = self.cheque_especial(saldo)

            if not cheque_especial:
                return False

        elif valor > 0:
            self._saldo -= valor
            print("Saque realizado com sucesso!")
            return True

        else:
            print("Erro: Valor informado é inválido.")

        return False

    def depositar(self, valor):
        if valor > 0:
            self._saldo += valor
            print("Depósito realizado com sucesso!")

        else:
            print("Erro: Valor informado é inválido.")
            return False

        return True

    def cheque_especial(self, salario):
        limite_cheque_especial = 0.20

        if salario >= 2000:
            limite = salario * limite_cheque_especial
            print(f"Você possui um limite de R$ {limite:.2f} disponível.")

        else:
            print("Você não possui limite de Cheque especial.")
            return False

        return True


class ContaCorrente(Conta):
    def __init__(self, numero, cliente, limite=500, limite_saques=3):
        super().__init__(numero, cliente)
        self.limite = limite
        self.limite_saques = limite_saques

    @classmethod
    def nova_conta(cls, cliente, numero):
        return cls(numero, cliente)

    def sacar(self, valor):
        numero_saque = len(
            [transacao for transacao in self.extrato.transacoes if transacao["tipo"] == Saque.__name__])

        excedeu_limite = valor > self.limite
        excedeu_saques = numero_saque >= self.limite_saques

        if excedeu_limite:
            print("Erro: O valor excede o limite.")

        elif excedeu_saques:
            print("Erro: Excedeu o limite de saques.")

        else:
            return super().sacar(valor)

        return False

    def __str__(self):
        return f"Agência:\t{self._agencia}\nC/C:\t\t{self._numero}\nTitular:\t{self.cliente.nome}"


class Extrato:
    def __init__(self):
        self._transacoes = []

    @property
    def transacoes(self):
        return self._transacoes

    def adicionar_transacao(self, transacao):
        self._transacoes.append({"tipo": transacao.__class__.__name__,
                                 "valor": transacao.valor,
                                 "data": datetime.now().strftime("%d-%m-%Y %H:%M:%S")})


class Transacao(ABC):
    @property
    @abstractmethod
    def valor(self):
        pass

    @abstractmethod
    def registrar(self, conta):
        pass


class Saque(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.sacar(self.valor)

        if sucesso_transacao:
            conta.extrato.adicionar_transacao(self)


class Deposito(Transacao):
    def __init__(self, valor):
        self._valor = valor

    @property
    def valor(self):
        return self._valor

    def registrar(self, conta):
        sucesso_transacao = conta.depositar(self.valor)

        if sucesso_transacao:
            conta.extrato.adicionar_transacao(self)


def menu():
    menu_text = """
    ================ MENU ================
    [1]\tDEPOSITAR
    [2]\tSACAR
    [3]\tEXTRATO
    [4]\tNOVO USUÁRIO
    [5]\tNOVA CONTA
    [6]\tLISTAR CONTAS
    [0]\tSAIR
    
    ==> """
    return input(textwrap.dedent(menu_text))


def filtrar_cliente(cpf, clientes):
    clientes_filtrados = [
        cliente for cliente in clientes if cliente.cpf == cpf]
    return clientes_filtrados[0] if clientes_filtrados else None


def recuperar_conta_cliente(cliente):
    if not cliente.contas:
        print("\nCliente não possui conta.\n\nCrie uma CONTA e tente novamente.\n\nVamos te redirecionar para o MENU principal.")
        return None

    return cliente.contas[0]


def depositar(cliente):
    valor = float(input("Informe o valor a ser depositado: "))
    transacao = Deposito(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def sacar(cliente):
    valor = float(input("Informe o valor a ser sacado: "))
    transacao = Saque(valor)

    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    cliente.realizar_transacao(conta, transacao)


def exibir_extrato(cliente):
    conta = recuperar_conta_cliente(cliente)
    if not conta:
        return

    print("\n============ EXTRATO ============")
    transacoes = conta.extrato.transacoes

    if not transacoes:
        print("Não foram realizadas movimentações.")
    else:
        for transacao in transacoes:
            print(f"\n{transacao['tipo']}:\n\tR$ {transacao['valor']:.2f}")

    print(f"\nSaldo:\n\tR$ {conta.saldo:.2f}")
    print("================================")


def criar_cliente(clientes, cpf):
    cliente = filtrar_cliente(cpf, clientes)

    if cliente:
        print("\nJá existe cliente com esse CPF.")
        return

    nome = input("Informe seu nome completo: ")
    if len(nome.split()) == 1:
        print("No campo NOME inserir o nome completo.")
        return criar_cliente(clientes, cpf)

    while True:
        data = input("Informe a data de nascimento (dd/mm/AAAA): ")
        try:
            data_nascimento = datetime.strptime(data, '%d/%m/%Y')
            break
        except ValueError:
            print("Formato de data inválido. Por favor, digite no formato dd/mm/AAAA.")
            return

    endereco = input("Informe seu endereço: ")

    cliente = PessoaFisica(
        nome=nome, data_nascimento=data_nascimento, cpf=cpf, endereco=endereco)
    clientes.append(cliente)

    numero_conta = random.randint(10000, 99999)
    conta = Conta.nova_conta(cliente, numero_conta)
    clientes[-1].contas.append(conta)
    print(
        f"\n**** Cliente criado com sucesso! ****\nAgência: {conta.agencia}\nNúmero da Conta: {numero_conta}")


def criar_conta(numero_conta, cliente, contas):
    conta = Conta.nova_conta(cliente, numero_conta)
    contas.append(conta)
    cliente.contas.append(conta)

    print("\n**** Conta criada com sucesso! ****")


def listar_contas(cliente):
    if not cliente.contas:
        print("\nNenhuma conta foi encontrada para esse cliente.")
        return

    print("\n========== LISTA DE CONTAS ==========")
    for conta in cliente.contas:
        print("=" * 70)
        print(f"Agência:\t{conta.agencia}\nConta Corrente:\t\t{conta.numero}\nTitular:\t{cliente.nome}")
    print("=" * 70)


def main():
    clientes = []
    contas = []

    print("Bem-vindo ao sistema bancário!")
    cliente = None

    while not cliente:
        cliente = login(clientes)
        if not cliente:
            opcao = input("Deseja criar um novo usuário? (s/n): ").lower()
            if opcao == 's':
                cpf = input("Informe o CPF: ")
                criar_cliente(clientes, cpf)
                cliente = None
            else:
                print("Encerrando o programa.")
                return

    while True:
        opcao = menu()

        if opcao == '1':
            depositar(cliente)

        elif opcao == '2':
            sacar(cliente)

        elif opcao == '3':
            exibir_extrato(cliente)

        elif opcao == '4':
            print("\nVocê já está logado como:", cliente.nome)

        elif opcao == '5':
            numero_conta = random.randint(10000, 99999)
            criar_conta(numero_conta, cliente, contas)

        elif opcao == '6':
            listar_contas(cliente)

        elif opcao == '0':
            print("\n<><><><><><> FINALIZANDO <><><><><><><>")
            print(f"\nObrigado por usar nossos serviços, {cliente.nome}!")
            print("\n=======================================")
            break

        else:
            print(
                "\nOperação inválida, por favor selecione novamente a operação desejada.")


def login(clientes):
    cpf = input("Informe seu CPF para login: ")
    cliente = filtrar_cliente(cpf, clientes)
    if not cliente:
        print("Cliente não encontrado.")
    return cliente


if __name__ == "__main__":
    main()
