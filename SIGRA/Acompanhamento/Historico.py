#  -*- coding: utf-8 -*-
#    @package: Historico.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re

from SIGRA import utils


def HEDIS(arquivo, encoding='utf-16'):
    '''Extrai as informações dos alunos matriculados em uma disciplina.

    Argumentos:
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    content = utils.load(arquivo, encoding)

    print('Extração de dados.')
    num_registros = 0
    REGEX = r'(\d\d/\d{3,}) +(\d{4}/\d+) +(\w+) +(\w\w) {2,}(.*)[\s\S]'
    relacao = {}
    for matricula, periodo, turma, mencao, nome in re.findall(REGEX, content):
        if periodo not in relacao:
            relacao[periodo] = {}
        if turma not in relacao[periodo]:
            relacao[periodo][turma] = {}
        relacao[periodo][turma][matricula] = {'Nome': nome, 'Menção': mencao}
        num_registros += 1

    print('{} registros.'.format(num_registros))
    return relacao
