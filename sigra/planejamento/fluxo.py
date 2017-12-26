#  -*- coding: utf-8 -*-
#    @package: fluxo.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from sigra import utils


def listagem(arquivo):
    '''Retorna um dicionário com as informações das disciplinas listadas no
    fluxo em cada período, extraindo as informações do arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Planejamento > Fluxo > FLULST
    '''
    def eh_novo_periodo(line):
        return parse_pre_requisitos(line) is not None

    def eh_tipo(line):
        return re.search(r'^ +\d{1,3} + (\w{3}) +\w$', line)

    def parse_credito(line):
        m = re.search(r'(\d{3})', line)
        return str(int(m.group(1)))

    def parse_disciplina(line):
        m = re.search(r'^ +?(\w{1,3}) +? (\d{6}) +? (\w.*)$', line)
        return m.group(1), m.group(2), m.group(3)

    def parse_pre_requisitos(line):
        m = re.search(r'^ +Período: +?(\d{1,3})'
                      ' +? Número de Créditos: +?(\d{1,3})$', line)
        if m:
            return int(m.group(1)), int(m.group(2))
        else:
            return None

    def parse_tipo(line):
        m = eh_tipo(line)
        return m.group(1)

    def preprocess(content):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Listagem de Fluxo de Curso - Dados Completos.*[\s\S]*?'
        FOOTER = r'^ + -{5,}[\s\S]+?lstflulst[\s\S]'

        content = re.sub(HEADER, '', content)
        content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line]

    content = preprocess(utils.load(arquivo))

    fluxo = {}
    i = 1
    num_lines = len(content)
    while i < num_lines:
        if eh_novo_periodo(content[i]):
            p, num_creditos = parse_pre_requisitos(content[i])
            periodo = {}

            i += 3

            while i < num_lines:
                if eh_novo_periodo(content[i]):
                    i -= 1
                    break

                if eh_tipo(content[i]):
                    tipo = parse_tipo(content[i])
                    if tipo not in periodo:
                        periodo[tipo] = {}

                    i += 1
                    dept, codigo, nome = parse_disciplina(content[i])

                    creditos = utils.Creditos.to_string(parse_credito(content[
                                                                      i + 1]),
                                                        parse_credito(content[
                                                                      i + 2]),
                                                        parse_credito(content[
                                                                      i + 3]),
                                                        parse_credito(content[
                                                                      i + 4]))
                    disciplina = {'nome': nome.title(),
                                  'dept': dept,
                                  'créditos': creditos}

                    i += 5
                    pr = ''
                    while i < num_lines:
                        if(eh_novo_periodo(content[i]) or eh_tipo(content[i])):
                            i -= 1
                            break

                        pr += ' '.join([content[i].strip(),
                                        content[i + 1].strip()])
                        i += 2

                        while (i < num_lines and
                               re.search(r'^ {120,}[\w\d].*?$', content[i])):
                            pr += ' ' + content[i].strip()
                            i += 1

                    pr = utils.parse_pre_requisitos(pr)
                    disciplina['pré-requisitos'] = pr

                    periodo[tipo][codigo] = disciplina

                i += 1

            fluxo[p] = periodo

        i += 1

    return fluxo
