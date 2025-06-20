﻿Sistema Bancário em Python

Este projeto é uma simulação de um sistema bancário simples desenvolvido em Python. O objetivo foi demonstrar a implementação de operações bancárias fundamentais como depósito, saque e extrato, além do gerenciamento de usuários e contas, aplicando regras de negócio específicas.

📖 Sobre o Projeto

O sistema foi construído de forma procedural e utiliza estruturas de dados em memória (listas e dicionários) para armazenar as informações dos usuários e das contas. Foi um projeto para praticar lógica de programação, manipulação de dados e estruturação de código em Python.

Funcionalidades Principais
* Menu Interativo: Navegação simples e intuitiva através de um menu no terminal.
* Operações Bancárias:
  * Depositar: Permite adicionar qualquer valor positivo a uma conta.
  * Sacar: Permite retirar dinheiro de uma conta, com as seguintes regras:
  * Limite de R$ 500,00 por saque.
  * Máximo de 3 saques por dia.
  * Extrato: Exibe o histórico de transações e o saldo atual da conta.
    
* Gerenciamento de Clientes:
  * Novo Usuário: Cadastra novos clientes (nome, data de nascimento, CPF e endereço). O CPF é único.
  * Nova Conta Corrente: Cria uma nova conta, vinculando-a a um usuário existente pelo CPF. As contas são numeradas sequencialmente.
  * Listar Contas: Mostra uma lista com todas as contas cadastradas, incluindo agência, número da conta e nome do titular.
  * Controle de Limites Diários: O sistema zera o contador de saques e transações diariamente, permitindo novas operações no dia seguinte.
