#  -*- coding: utf-8 -*-
#    @package: Alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re

from SIGRA import utils


def ALUREL(arquivo):
    '''Retorna um dicionário com as informações de cada aluno listado no
    arquivo com a relação de alunos.

    Argumentos:
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUTEL
    '''
    content = utils.load(arquivo)

    relacao = {}

    print('Extração de dados.')
    num_registros = 0
    REGEX = r'(\d\d/\d{3,}) +(.*?) {2,}(\d+/\d+) {2,}(\w+) +(\d+) +(.*)[\s\S]'
    for (matricula, nome, periodo,
         ingresso, codigo, opcao) in re.findall(REGEX, content):
        if codigo not in relacao:
            relacao[codigo] = {'Opção': opcao, 'Alunos': {}}
        if periodo not in relacao[codigo]['Alunos']:
            relacao[codigo]['Alunos'][periodo] = {}
        aluno = {'Nome': nome, 'Ingresso': ingresso}
        relacao[codigo]['Alunos'][periodo][matricula] = aluno
        num_registros += 1

    print('{} registros.'.format(num_registros))
    return relacao


def ALUTEL(arquivo):
    '''Extrai o nome completo, telefone de contato e o e-mail registrados
    para cada aluno(a) listado(a) no arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUTEL
    '''
    content = utils.load(arquivo)

    relacao = {}
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
