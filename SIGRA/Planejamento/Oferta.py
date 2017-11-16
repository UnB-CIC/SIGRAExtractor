#  -*- coding: utf-8 -*-
#    @package: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from SIGRA import utils


def OFELST(arquivo):
    '''Retorna um dicionário com as informações de cada disciplina
    ofertada, extraindo as informações do arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST

    No caso de pré-requisitos, o resultado é uma lista em que cada item
    tem uma relação 'OU' com os demais, e cada item é uma lista cujos
    itens têm uma relação 'E' entre si. Por exemplo, a listagem da
    disciplina 116858 - Informática Aplicada a Educação, seria a lista
    [['116343'], ['125172', '194531']], que deve ser interpretada como
    116343 OU (125172 E 194531). Ou seja, para matrícula na disciplina
    116858, é preciso ter sido aprovado na disciplina 'Linguagens de
    Programação' ou ter sido aprovado em ambas as disciplinas
    'Aprendizagem e Ensino' e 'Didática Fundamental'.
    '''
    def clean_file_content(arquivo):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Período :.*\d{4}/\d.*[\s\S]'
        FOOTER = r' Observações :[.*|\s\S]+?lstofelst'

        content = utils.load(arquivo)
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
        return {'Teoria': int(m.group(1)), 'Prática': int(m.group(2)),
                'Extensão': int(m.group(3)), 'Estudo': int(m.group(4))}

    def parse_disciplina(line):
        codigo, nome = line.split('  -  ')
        return codigo.strip(), utils.capitalize(nome.strip())

    def parse_pre_requisitos(line):
        m = re.search(r'(\w{3}-\d{6}  .*$)', line)
        return m.group(0) if m else ''

    def parse_Prof_Reserva_Obs(line):
        if '  ' in line:
            i = line.index('  ')
            professor = line[:i]
            line = line[i:].strip()
        else:
            professor = line.strip()

        m = re.search(r'(\w.*?)/(\d+)[ \s\S]', professor)
        if m:
            if '   ' in m.group(1):
                split = m.group(1).split('   ')
                professor = split[0]
                for x in range(1, len(split)):
                    m = re.search(r'(\w.*?)/(\d+)[ \s\S]', split[x])
                    if m:
                        reserva = {m.group(1): int(m.group(2))}
                        break
            else:
                professor = ''
                reserva = {m.group(1): int(m.group(2))}
        else:
            m = re.search(r'(\w.*?)/(\d+)[ \s\S]', line)
            if m:
                reserva = {m.group(1).split('   ')[-1]: int(m.group(2))}
            else:
                reserva = {}
            # reserva = {m.group(1): int(m.group(2))} if m else {}

        m = re.search(r'(\*+)[ \s\S]', line)
        obs = m.group(1) if m else ''
        return professor, reserva, obs

    def parse_turma(line):
        TURNO = r'(Diurno|Noturno|Ambos)'
        DIA = r'(Segunda|Terça|Quarta|Quinta|Sexta|Sábado|Domingo)'
        HORARIO = r'(\d\d:\d\d \d\d:\d\d)'
        # REGEX = r'^ +([A-Z]{1,3}) (.*?) (\d+) +' + TURNO + ' +' \
        #         '' + DIA + ' +' + HORARIO + ' (.*?)  +(.*)'
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
                professor, reserva, obs = parse_Prof_Reserva_Obs(line)

        aula = {dia: {'horário': horario, 'local': local}} if dia else {}
        return (t, descricao, vagas, turno, aula, professor, reserva, obs)

    content = clean_file_content(arquivo)

    oferta = {}

    print('Extração de dados.')
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
    print('{} disciplinas, {} turmas'.format(num_disciplinas, num_turmas))

    return oferta
