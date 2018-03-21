#  -*- coding: utf-8 -*-
#    @package: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from sigra import utils


class TurmaOfertada():
    def __init__(self, turma, descricao, vagas, turno, aulas,
                 professores, reserva='', observacoes=''):
        self.turma = turma
        self.descricao = descricao
        self.vagas = vagas
        self.turno = turno
        self.aulas = aulas if isinstance(aulas, dict) else {aulas.dia: aulas}
        self.professores = professores
        self.reserva = reserva
        self.observacoes = observacoes

    def __repr__(self):
        return '{} {}'.format(self.turma,
                              ','.join(str(a) for a in self.aulas if a))


class DisciplinaOfertada(utils.Disciplina):
    def __init__(self, depto, codigo, nome, creditos,
                 pre_requisitos=[], turmas={}):
        super().__init__(depto, codigo, nome, creditos, pre_requisitos)
        self.turmas = turmas

    def __repr__(self):
        turmas = '\n\t'.join(t + ' ' + self.turmas[t]
                             for t in sorted(self.turmas))
        return '{}\n\t{}'.format(super().__repr__(), turmas)


def listagem(arquivo):
    '''Retorna um dicionário com as informações de cada disciplina
    ofertada, extraindo as informações do arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST

    No caso de pré-requisitos, veja a função utils.parse_pre_requisitos.

    @to-do Separação por centro de custo.
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
        return '{}:{}:{}:{}'.format(int(m.group(1)),
                                    int(m.group(2)),
                                    int(m.group(3)),
                                    int(m.group(4)))

    def parse_disciplina(line):
        codigo, nome = line.split('  -  ')
        return codigo.strip(), nome.strip().title()

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

        aula = {dia: {horario: local}} if dia else {}
        return t, TurmaOfertada(t, descricao, vagas, turno, aula, professor,
                                reserva, obs)

    lines = preprocess(utils.load(arquivo))

    oferta = {}

    i = 1
    num_lines = len(lines)
    while i < num_lines:
        if eh_disciplina(lines[i]):
            codigo, nome = parse_disciplina(lines[i])

            i += 1
            if codigo not in oferta:
                oferta[codigo] = DisciplinaOfertada('',
                                                    codigo,
                                                    nome,
                                                    parse_creditos(lines[i]),
                                                    [],
                                                    {})
            # ### Pré-requisitos ###
            pre_reqs = ''
            while not lines[i].startswith('   Turma'):
                pre_reqs += parse_pre_requisitos(lines[i])

                i += 1

            p = []
            for opcoes in pre_reqs.split('OU'):
                p.append(re.findall(r'\d{6}', opcoes))
            oferta[codigo].pre_requisitos = p
            # ### Pré-requisitos ###

            # ### Turmas ###
            turmas = {}

            i += 1
            while i < num_lines and eh_nova_turma(lines[i]):
                t, info = parse_turma(lines[i])
                turmas[t] = info

                i += 1
                while i < num_lines and not eh_nova_turma(lines[i]):
                    if eh_disciplina(lines[i]):
                        break

                    _, info = parse_turma(lines[i])

                    if info.descricao:
                        turmas[t].descricao += ' ' + info.descricao
                    for dia in info.aulas:
                        if dia in turmas[t].aulas:
                            turmas[t].aulas[dia].update(info.aulas[dia])
                        else:
                            turmas[t].aulas.update(info.aulas)
                    if info.professores:
                        if len(info.professores.split()) == 1:
                            # Supondo que haja um professor com nome muito
                            # longo, a última parte se estende em uma nova
                            # linha
                            turmas[t].professores += ' ' + info.professores
                        else:
                            # É um nome composto de pelo menos duas partes,
                            # supõe-se que seja de um novo professor
                            turmas[t].professores += ', ' + info.professores
                    if info.reserva:
                        turmas[t].reserva.update(info.reserva)
                    if info.observacoes:
                        turmas[t].observacoes += ' ' + info.observacoes

                    i += 1

            if not oferta[codigo].turmas:
                oferta[codigo].turmas = turmas
            else:
                oferta[codigo].turmas.update(turmas)
            # ### Turmas ###

        if i < num_lines and not eh_disciplina(lines[i]):
            i += 1

    num_disciplinas = len(oferta)
    num_turmas = sum(len(oferta[codigo].turmas) for codigo in oferta)
    print('{} disciplinas ({} turmas) ofertadas.'.format(num_disciplinas,
                                                         num_turmas))

    return oferta
