#  -*- coding: utf-8 -*-
#    @package: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
# @disciplina: Algoritmos e Programação de Computadores
#
# Funções de utilitárias.

from re import findall


def capitalize(string):
    '''Retorna o string dado com todas as palavras iniciando com letra
    maiúscula.'''
    return ' '.join(s.capitalize() for s in string.split())


def creditos2str(teoria, pratica, extensao, estudo):
    '''Retorna um string com a representação dos créditos de uma disciplina.'''
    return '{}:{}:{}:{}'.format(int(teoria), int(pratica), int(extensao),
                                int(estudo))


def load(arquivo):
    '''Lê o conteúdo do arquivo (UTF-16) dado e o retorna.'''
    print('Leitura dos dados de {}.'.format(arquivo))

    with open(arquivo, encoding='utf-16') as f:
        content = f.read()

    return content


def parse_pre_requisitos(pre_reqs):
    '''Processa um string de pré-requisitos (separados por 'E' e 'OU'), e
    retorna uma lista em que cada item tem uma relação 'OU' com os demais, e
    cada item é uma lista cujos itens têm uma relação 'E' entre si. Por
    exemplo, a listagem da disciplina 116858 - Informática Aplicada a Educação,
    seria a lista [['116343'], ['125172', '194531']], que deve ser interpretada
    como 116343 OU (125172 E 194531). Ou seja, para matrícula na disciplina
    116858, é preciso ter sido aprovado na disciplina 'Linguagens de
    Programação' ou ter sido aprovado em ambas as disciplinas 'Aprendizagem e
    Ensino' e 'Didática Fundamental'.
    '''
    pre_requisitos = []
    for opcoes in pre_reqs.split('OU'):
        pre_requisitos.append(findall(r'\d{6}', opcoes))
    return [p for p in pre_requisitos if p]


def str2creditos(string):
    '''Retorna um dicionário contendo a separação de créditos por tipo.'''
    creditos = string.split(':')
    return {'Teoria': int(creditos[0]),
            'Prática': int(creditos[1]),
            'Extensão': int(creditos[2]),
            'Estudo': int(creditos[3])}
