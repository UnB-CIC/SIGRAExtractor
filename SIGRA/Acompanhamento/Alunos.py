#  -*- coding: utf-8 -*-
#    @package: Alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re


def ALUREL(arquivo, encoding='utf-16'):
    print('Leitura dos dados de {}.'.format(arquivo))

    relacao = {}
    with open(arquivo, encoding=encoding) as f:
        content = f.read()

    print('Extração de dados.')
    num_registros = 0
    REGEX = r'(\d\d/\d{3,}) +(.*?) {2,}(\d+/\d+) {2,}(\w+) +(\d+) +(.*)[\s\S]'
    for matricula, nome, periodo, forma_de_ingresso, codigo_opcao, nome_opcao in re.findall(REGEX, content):
        if codigo_opcao not in relacao:
            relacao[codigo_opcao] = {'Opção': nome_opcao, 'Alunos': {}}
        if periodo not in relacao[codigo_opcao]['Alunos']:
            relacao[codigo_opcao]['Alunos'][periodo] = {}
        relacao[codigo_opcao]['Alunos'][periodo][matricula] = {'Nome': nome, 'Ingresso': forma_de_ingresso}
        num_registros += 1

    print('{} registros.'.format(num_registros))
    return relacao


def ALUTEL(arquivo, encoding='utf-16'):
    '''Extrai o nome completo, telefone de contato e o e-mail registrados
    para cada aluno(a) listado(a) no arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUTEL
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    print('Leitura dos dados de {}.'.format(arquivo))
    relacao = {}
    with open(arquivo, encoding=encoding) as f:
        content = f.read()

    print('Extração de dados.')
    REGEX = r'(\d\d/\d{5,})[ ]+(\w.*)\n[ ]+(\w.*@.*)'
    for matricula, nome_e_tel, email in re.findall(REGEX, content):
        if '   ' in nome_e_tel:
            infos = nome_e_tel.split('   ')
            nome, telefone = infos[0].strip(), infos[-1].strip()
        else:
            nome, telefone = nome_e_tel, ''
        relacao[matricula] = {'nome': nome, 'e-mail': email,
                              'telefone': telefone}

    print('{} registros.'.format(len(relacao)))
    return relacao
