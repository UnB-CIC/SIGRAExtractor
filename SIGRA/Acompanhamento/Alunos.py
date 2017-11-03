#  -*- coding: utf-8 -*-
#    @package: acompanhamento.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re


def ALUTEL(in_file, encoding='ISO-8859-1'):
    '''Extrai o nome completo, telefone de contato e o e-mail registrados
    para cada aluno(a) listado(a) no arquivo de entrada.

    Argumentos:
    in_file -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUTEL
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    print('Leitura dos dados de {}.'.format(in_file))
    relacao = {}
    with open(in_file, encoding=encoding) as f:
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
