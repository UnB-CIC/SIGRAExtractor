#  -*- coding: utf-8 -*-
#    @package: alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re

from sigra import utils


def contatos(arquivo):
    '''Extrai o nome completo, telefone de contato e o e-mail registrados
    para cada aluno(a) listado(a) no arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUTEL
    '''
    def parse_info(match_obj):
        matricula, nome_e_tel, email = match_obj
        if '   ' in nome_e_tel:
            infos = nome_e_tel.split('   ')
            nome, telefone = infos[0].strip(), infos[-1].strip()
        else:
            nome, telefone = nome_e_tel, ''
        return (matricula, {'nome': nome,
                            'e-mail': email,
                            'telefone': telefone})

    content = utils.load(arquivo)

    REGEX = r'(\d\d/\d{5,}) +(\w.*)\n +(\w.*@.*)'
    contatos = dict(parse_info(match_obj)
                    for match_obj in re.findall(REGEX, content))

    print('{} contatos.'.format(len(contatos)))
    return contatos


def relacao(arquivo):
    '''Retorna um dicionário com as informações de cada aluno listado no
    arquivo com a relação de alunos.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Acompanhamento > Alunos > ALUREL
    '''
    content = utils.load(arquivo)

    relacao = {}

    num_registros = 0
    REGEX = r'(\d\d/\d{3,}) +(.*?) {2,}(\d+/\d+) {2,}(\w+) +(\d+) +(.*)[\s\S]'
    for (matricula,
         nome,
         periodo_ingresso,
         forma_ingresso,
         codigo,
         nome_opcao) in re.findall(REGEX, content):
        if codigo not in relacao:
            relacao[codigo] = {'Nome da Opção': nome_opcao, 'Alunos': {}}
        if periodo_ingresso not in relacao[codigo]['Alunos']:
            relacao[codigo]['Alunos'][periodo_ingresso] = {}
        aluno = {'Nome': nome, 'Forma Ingresso': forma_ingresso}
        relacao[codigo]['Alunos'][periodo_ingresso][matricula] = aluno
        num_registros += 1

    print('{} alunos relacionados.'.format(num_registros))
    return relacao
