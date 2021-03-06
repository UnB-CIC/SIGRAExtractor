#  -*- coding: utf-8 -*-
#    @package: curso.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from sigra import utils


def estatisticas(arquivos):
    '''Retorna um dicionário com as informações de entrada/saída de alunos
    para cada período no(s) arquivo(s) de entrada.

    Argumentos:
    arquivos -- lista contendo o caminho para cada arquivo (UTF-16) contendo os
                dados, que deve ser o relatório exportado via:
                SIGRA > Planejamento > Curso > CUREGEP
    '''
    def lista_periodos(line):
        REGEX = r'^ +(\d{4}/\d) +(\d{4}/\d) +(\d{4}/\d) +(\d{4}/\d)$'
        return re.search(REGEX, line)

    def parse_periodos(line):
        return list(lista_periodos(line).groups())

    def lista_estatistica(line):
        REGEX = r'^ +\d+  (.*?)  +(\d+) +(\d+) +(\d+) +(\d+)' \
                ' +(\d+) +(\d+) +(\d+) +(\d+)$'
        return re.search(REGEX, line)

    def parse_estatistica(line):
        return list(lista_estatistica(line).groups())

    stats = {}
    for arquivo in arquivos:
        lines = utils.load(arquivo).split('\n')

        i = 0
        while not lista_periodos(lines[i]):
            i += 1

        periodos = parse_periodos(lines[i])
        for p in periodos:
            stats[p] = {}

        while not lista_estatistica(lines[i]):
            i += 1
        while lista_estatistica(lines[i]):
            estatistica = parse_estatistica(lines[i])

            s = 1
            for p in periodos:
                stats[p][estatistica[0]] = {'Mas': estatistica[s],
                                            'Fem': estatistica[s + 1]}
                s += 2

            i += 1

    print('Estatísticas de {} semestres.'.format(len(stats)))

    return stats
