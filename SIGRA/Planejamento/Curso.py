#  -*- coding: utf-8 -*-
#    @package: curso.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re


def CUREST(in_files, encoding='utf-16'):
    raise NotImplementedError


def CUREGEP(in_files, encoding='utf-16'):
    '''Retorna um dicionário com as informações de entrada/saída de alunos
    para cada período no(s) arquivo(s) de entrada.

    Argumentos:
    in_file -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Planejamento > Curso > CUREGEP
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    def lista_periodos(line):
        REGEX = r'^ +(\d{4}/\d) +(\d{4}/\d) +(\d{4}/\d) +(\d{4}/\d)$'
        return re.search(REGEX, line)

    def parse_periodos(line):
        return [p for p in lista_periodos(line).groups()]

    def lista_estatistica(line):
        REGEX = r'^ +\d+  (.*?)  +(\d+) +(\d+) +(\d+) +(\d+)' \
                ' +(\d+) +(\d+) +(\d+) +(\d+)$'
        return re.search(REGEX, line)

    def parse_estatistica(line):
        return [e for e in lista_estatistica(line).groups()]

    stats = {}
    for in_file in in_files:
        print('Leitura dos dados de {}.'.format(in_file))

        with open(in_file, encoding=encoding) as f:
            content = f.readlines()

        i = 0
        while not lista_periodos(content[i]):
            i += 1

        periodos = parse_periodos(content[i])
        for p in periodos:
            stats[p] = {}

        while not lista_estatistica(content[i]):
            i += 1
        while lista_estatistica(content[i]):
            stat = parse_estatistica(content[i])

            s = 1
            for p in periodos:
                stats[p][stat[0]] = {'Mas': stat[s],
                                     'Fem': stat[s + 1]}
                s += 2

            i += 1

    print('{} semestres.'.format(len(stats)))

    return stats
