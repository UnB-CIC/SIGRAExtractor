#  -*- coding: utf-8 -*-
#    @package: fluxo.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from sigra import utils


class PeriodoDoFluxo():
    def __init__(self, numero, creditos, disciplinas={}):
        self.numero = numero
        self.creditos = creditos
        self.disciplinas = disciplinas

    def __repr__(self):
        disciplinas = ''.join('\n\t{} {} {}'.format(tipo, codigo, descricao)
                              for tipo, disciplinas in self.disciplinas.items()
                              for codigo, descricao in disciplinas.items())

        return 'Período {} ({} créditos){}'.format(self.numero,
                                                   self.creditos,
                                                   disciplinas)


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

    def eh_modalidade(line):
        return re.search(r'^ +\d{1,3} + (\w{3}) +\w$', line)

    def eh_pre_requisito(line):
        return not (eh_novo_periodo(line) or eh_modalidade(line))

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

    def parse_modalidade(line):
        m = eh_modalidade(line)
        return m.group(1)

    def preprocess(content):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Listagem de Fluxo de Curso - Dados Completos.*[\s\S]*?'
        FOOTER = r'^ + -{5,}[\s\S]+?lstflulst[\s\S]'

        content = re.sub(HEADER, '', content)
        content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line]

    lines = preprocess(utils.load(arquivo))

    fluxo = {}
    i = 1
    num_lines = len(lines)
    while i < num_lines:
        if eh_novo_periodo(lines[i]):
            p, num_creditos = parse_pre_requisitos(lines[i])
            disciplinas = {}

            i += 3  # Pulando o cabeçalho

            while i < num_lines:
                if eh_novo_periodo(lines[i]):
                    i -= 1
                    break

                if eh_modalidade(lines[i]):
                    tipo = parse_modalidade(lines[i])
                    if tipo not in disciplinas:
                        disciplinas[tipo] = {}

                    i += 1
                    dept, codigo, nome = parse_disciplina(lines[i])
                    creditos = ':'.join([parse_credito(lines[i + 1]),
                                         parse_credito(lines[i + 2]),
                                         parse_credito(lines[i + 3]),
                                         parse_credito(lines[i + 4])])

                    i += 5
                    pr = ''
                    while i < num_lines:
                        if not eh_pre_requisito(lines[i]):
                            i -= 1
                            break

                        pr += ' '.join([lines[i].strip(),
                                        lines[i + 1].strip()])
                        i += 2

                        while (i < num_lines and
                               re.search(r'^ {120,}[\w\d].*?$', lines[i])):
                            pr += ' ' + lines[i].strip()
                            i += 1

                    pr = utils.parse_pre_requisitos(pr)
                    disciplinas[tipo][codigo] = utils.Disciplina(dept,
                                                                 codigo,
                                                                 nome.title(),
                                                                 creditos,
                                                                 pr)

                i += 1

            fluxo[p] = PeriodoDoFluxo(p, num_creditos, disciplinas)
        i += 1

    return fluxo
