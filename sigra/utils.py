#  -*- coding: utf-8 -*-
#    @package: utils.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
# @disciplina: Algoritmos e Programação de Computadores
#
# Funções de utilitárias.

import re


class Creditos():
    def __init__(self, teoria, pratica, extensao, estudo):
        self.teoria = int(teoria)
        self.pratica = int(pratica)
        self.extensao = int(extensao)
        self.estudo = int(estudo)

    def total(self, considera_estudo=False):
        total = self.teoria + self.pratica + self.extensao
        if considera_estudo:
            total += self.estudo
        return total

    def __repr__(self):
        return '{}:{}:{}:{}'.format(self.teoria, self.pratica,
                                    self.extensao, self.estudo)


class Disciplina():
    def __init__(self, depto, codigo, nome, creditos, pre_requisitos=[]):
        self.depto = depto
        self.codigo = codigo
        self.nome = nome
        self.creditos = creditos
        self.pre_requisitos = pre_requisitos

    def __repr__(self):
        return '({}) {} - {} ({})'.format(self.depto,
                                          self.codigo,
                                          self.nome,
                                          str(self.creditos))


def load(arquivo, encoding='utf-16'):
    '''Lê o conteúdo do arquivo dado e o retorna.'''
    if not arquivo.endswith('.txt'):
        arquivo += '.txt'

    print('Leitura de {}.'.format(arquivo))
    with open(arquivo, encoding=encoding) as f:
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
        pre_requisitos.append(re.findall(r'\d{6}', opcoes))
    return [p for p in pre_requisitos if p]
