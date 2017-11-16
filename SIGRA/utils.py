#  -*- coding: utf-8 -*-
#    @package: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
# @disciplina: Algoritmos e Programação de Computadores
#
# Funções de utilitárias.


def capitalize(string):
    '''Retorna o string dado com todas as palavras iniciando com letra
    maiúscula.'''
    return ' '.join(s.capitalize() for s in string.split())


def load(arquivo):
    '''Lê o conteúdo do arquivo dado e o retorna.'''
    print('Leitura dos dados de {}.'.format(arquivo))

    with open(arquivo, encoding='utf-16') as f:
        content = f.read()

    return content
