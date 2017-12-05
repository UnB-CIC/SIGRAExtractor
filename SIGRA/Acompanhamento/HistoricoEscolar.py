#  -*- coding: utf-8 -*-
#    @package: HistoricoEscolar.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Acompanhamento do Sistema
# de Graduação da UnB (SIGRA).

import re

from SIGRA import utils


def AlunosQueCursaramDisciplina(arquivo):
    '''Extrai as informações dos alunos que cursaram determinada disciplina.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    '''
    content = utils.load(arquivo)

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


def EstatisticaDeMencoes(arquivo):
    '''Extrai as informações do histórico de menções de disciplinas.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Acompanhamento > Histórico Escolar > HEEME
    '''
    def preprocess(content):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Histórico Escolar: Estatística de Menções?'
        FOOTER = r'  --+[\s\S].*lstheeme'

        content = re.sub(HEADER, '', content)
        content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line.strip()]

    def eh_disciplina(line):
        return re.search(r'^ +Período:$', line)

    def eh_total(line):
        return re.search(r'^ +TOTAL DE MENÇÕES +(\d+)$', line)

    def parse_codigo(line):
        return re.search(r'^ +(\d{6})$', line).group(1)

    def parse_departamento(line):
        return re.search(r'^ +Disciplina: +(\w+)$', line).group(1)

    def parse_nivel(line):
        return re.search(r'^ +(\w+) -$', line).group(1)

    def parse_nome(line):
        return re.search(r'^ +(\w.*)$', line).group(1)

    def parse_periodo(line):
        return re.search(r'^ +(\d{4}/\d)$', line).group(1)

    def parse_total_de_mencoes(line):
        return int(eh_total(line).group(1))

    def parse_turma(line):
        return line.split('Turma:')[-1].strip()

    content = preprocess(utils.load(arquivo))

    print('Extração de dados.')
    relacao = {}
    num_disciplinas, num_turmas = 0, 0
    i = 1
    num_lines = len(content)
    while i < num_lines:
        if eh_disciplina(content[i]):
            periodo = parse_periodo(content[i + 1])
            depto = parse_departamento(content[i + 2])
            codigo = parse_codigo(content[i + 4])
            nivel = parse_nivel(content[i + 6])
            # nome = parse_nome(content[i + 7])
            turma = parse_turma(content[i + 8])

            i += 9
            while i < num_lines and not eh_total(content[i]):
                i += 1

            if i < num_lines:
                mencoes = parse_total_de_mencoes(content[i])

                if periodo not in relacao:
                    relacao[periodo] = {depto: {}}
                if codigo not in relacao[periodo][depto]:
                    num_disciplinas += 1
                    relacao[periodo][depto][codigo] = {'Nível': nivel,
                                                       'Turmas': {}}

                num_turmas += 1
                relacao[periodo][depto][codigo]['Turmas'][turma] = mencoes

        i += 1

    print('{} disciplinas, {} turmas.'.format(num_disciplinas, num_turmas))
    return relacao
