#  -*- coding: utf-8 -*-
#    @package: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from sigra import utils


def listagem(arquivo):
    '''Retorna um dicionário com as informações de cada disciplina
    ofertada, extraindo as informações do arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST

    No caso de pré-requisitos, veja a função utils.parse_pre_requisitos.
    '''
    def preprocess(content):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Período :.*\d{4}/\d.*[\s\S]'
        FOOTER = r' Observações :[.*|\s\S]+?lstofelst'

        content = re.sub(HEADER, '', content)
        content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line]

    def eh_disciplina(line):
        return re.search(r'^.{10,14} -  \w+', line)

    def eh_nova_turma(line):
        REGEX = r'^  ([A-Z]{1,2}) .*?(\d+) +(Diurno|Noturno|Ambos)'
        return re.search(REGEX, line)

    def parse_creditos(line):
        CREDITOS = r'(\d{3})  -   (\d{3})   -   (\d{3})  -   (\d{3})'
        m = re.search(CREDITOS, line)
        return utils.Creditos.to_string(m.group(1), m.group(2),
                                        m.group(3), m.group(4))

    def parse_disciplina(line):
        codigo, nome = line.split('  -  ')
        return codigo.strip(), utils.capitalize(nome.strip())

    def parse_pre_requisitos(line):
        m = re.search(r'(\w{3}-\d{6}  .*$)', line)
        return m.group(0) if m else ''

    def parse_Prof_Reserva_Obs(line):
        professor = ''
        reserva = {}
        obs = ''

        partes = [p.strip() for p in line.split('   ') if p.strip()]

        for parte in partes:
            m = re.search(r'^(.*)/(\d+)$', parte)
            if m:
                reserva[m.group(1)] = int(m.group(2))
            else:
                m = re.search(r'^(\*+)$', parte)
                if m:
                    obs = m.group(1)
                else:
                    professor = parte
        return professor, reserva, obs

    def parse_turma(line):
        TURNO = r'(Diurno|Noturno|Ambos)'
        DIA = r'(Segunda|Terça|Quarta|Quinta|Sexta|Sábado|Domingo)'
        HORARIO = r'(\d\d:\d\d \d\d:\d\d)'
        REGEX = r'^ +([A-Z]{1,3}) (.*?) (\d+) +' + TURNO + '(.*)'

        m = re.search(REGEX, line)
        if m:  # nova turma
            t = m.group(1)
            descricao = m.group(2).strip()
            vagas = int(m.group(3))
            turno = m.group(4)
            restante = m.group(5).strip()

            m = re.search(DIA + ' +' + HORARIO + ' (.*?)  +(.*)', restante)
            if m:
                dia = m.group(1)
                horario = m.group(2)
                local = m.group(3)
                restante = m.group(4)
            else:
                dia, horario, local = '', '', ''

            professor, reserva, obs = parse_Prof_Reserva_Obs(restante)
        else:
            t = ''
            vagas = ''
            turno = ''

            m = re.search(r'(.*)' + DIA + ' +' + HORARIO + ' (.*)', line)
            if m:  # tem dia
                descricao = m.group(1).strip()
                dia = m.group(2)
                horario = m.group(3)
                restante = m.group(4).strip()

                if '  ' in restante:  # tem professor ou reserva ou obs
                    i = restante.index('  ')
                    local = restante[:i]
                    restante = restante[i:].strip()
                    professor, reserva, obs = parse_Prof_Reserva_Obs(restante)
                else:
                    local = restante
                    professor, reserva, obs = '', '', ''

            else:
                descricao = line[7:36].strip()
                dia, horario, local = '', '', ''
                professor, reserva, obs = '', '', ''
                if len(line) > 36:
                    professor, reserva, obs = parse_Prof_Reserva_Obs(line[36:])

        aula = {dia: {'horário': horario, 'local': local}} if dia else {}
        return (t, descricao, vagas, turno, aula, professor, reserva, obs)

    content = preprocess(utils.load(arquivo))

    oferta = {}

    i = 1
    num_lines = len(content)
    while i < num_lines:
        if eh_disciplina(content[i]):
            codigo, nome = parse_disciplina(content[i])
            if codigo not in oferta:
                oferta[codigo] = {'nome': nome}

            # ### Pré-requisitos ###
            i += 1
            oferta[codigo]['créditos'] = parse_creditos(content[i])

            pre_reqs = ''
            while not content[i].startswith('   Turma'):
                pre_reqs += parse_pre_requisitos(content[i])

                i += 1

            p = []
            for opcoes in pre_reqs.split('OU'):
                p.append(re.findall(r'\d{6}', opcoes))
            oferta[codigo]['pré-requisitos'] = p
            # ### Pré-requisitos ###

            # ### Turmas ###
            turmas = {}

            i += 1
            while i < num_lines and eh_nova_turma(content[i]):
                (t, descricao, vagas, turno,
                 aula, professor, reserva, obs) = parse_turma(content[i])
                turmas[t] = {'descrição': descricao, 'vagas': vagas,
                             'turno': turno, 'aulas': [aula],
                             'professores': professor,
                             'reserva': reserva, 'observação': obs}

                i += 1
                while i < num_lines and not eh_nova_turma(content[i]):
                    if eh_disciplina(content[i]):
                        break

                    (_, descricao, vagas, turno,
                     aula, professor, reserva, obs) = parse_turma(content[i])

                    if descricao:
                        turmas[t]['descrição'] += ' ' + descricao
                    if aula:
                        turmas[t]['aulas'].append(aula)
                    if professor:
                        if len(professor.split()) == 1:
                            # Supondo que haja um professor com nome muito
                            # longo, a última parte se estende em uma nova
                            # linha
                            turmas[t]['professores'] += ' ' + professor
                        else:
                            # É um nome composto de pelo menos duas partes,
                            # supõe-se que seja de um novo professor
                            turmas[t]['professores'] += ', ' + professor
                    if reserva:
                        turmas[t]['reserva'].update(reserva)
                    if obs:
                        turmas[t]['observação'] += ' ' + obs

                    i += 1

            if 'turmas' not in oferta[codigo]:
                oferta[codigo]['turmas'] = turmas
            else:
                oferta[codigo]['turmas'].update(turmas)
            # ### Turmas ###

        if i < num_lines and not eh_disciplina(content[i]):
            i += 1

    num_disciplinas = len(oferta)
    num_turmas = sum(len(oferta[codigo]['turmas']) for codigo in oferta)
    print('{} disciplinas ({} turmas) ofertadas.'.format(num_disciplinas,
                                                         num_turmas))

    return oferta
