#  -*- coding: utf-8 -*-
#    @package: oferta.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de planejamento do fluxo do
# Sistema de Graduação da UnB (SIGRA).


import re
from SIGRA import utils


def OFELST(in_file, encoding='utf-16'):
    '''Retorna um dicionário com as informações de cada disciplina
    ofertada, extraindo as informações do arquivo de entrada.

    Argumentos:
    in_file -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)

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
    def clean_file_content(file_name, encoding):
        HEADER = r'Universidade de Brasília.*[\s\S]*?' \
                 'Período :.*\d{4}/\d.*[\s\S]'
        FOOTER = r' Observações :[.*|\s\S]+?lstofelst'

        with open(file_name, encoding=encoding) as f:
            content = re.sub(HEADER, '', f.read())
            content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line]

    def eh_disciplina(line):
        return re.search(r'^.{10,14} -  \w+', line)

    def eh_nova_turma(line):
        return re.search(r'^  [A-Z]{1,2} *?\w+', line)

    def parse_creditos(line):
        CREDITOS = r'(\d{3})  -   (\d{3})   -   (\d{3})  -   (\d{3})'
        m = re.search(CREDITOS, line)
        return {'Teoria': int(m.group(1)), 'Prática': int(m.group(2)),
                'Extensão': int(m.group(3)), 'Estudo': int(m.group(4))}

    def parse_disciplina(line):
        codigo, nome = line.split('  -  ')
        return codigo.strip(), nome.strip()

    def parse_pre_requisitos(line):
        m = re.search(r'(\w{3}-\d{6}  .*$)', line)
        return m.group(0) if m else ''

    def parse_turma(line):
        t = line[:7].strip()
        descricao = line[7:36].strip()
        vagas = line[36:41].strip()
        turno = line[41:54].strip()
        dia = line[54:62].strip()
        horario = line[62:74].strip()
        local = line[74:115].strip()
        aula = {dia: {'horário': horario, 'local': local}}
        if len(line) < 160:
            professor = utils.capitalize(line[115:].strip())
            reserva = ''
            obs = ''
        else:
            professor = utils.capitalize(line[115:160].strip())
            if len(line) < 224:
                reserva = line[160:].strip()
                obs = ''
            else:
                reserva = line[160:224].strip()
                obs = line[224:].strip()
        return (t, descricao, vagas, turno, aula, professor, reserva,
                obs)

        # (.*?) + -  (.*?)[\s\S] .*?-+ Disciplinas do Departamento[\s\S](.*?)
    content = clean_file_content(in_file, encoding)
    for line in content:
        print(line)
    exit(1)

    print('Leitura dos dados de {}.'.format(in_file))
    content = clean_file_content(in_file, encoding)

    oferta = {}

    print('Extração de dados.')
    i = 1
    num_lines = len(content)
    while i < num_lines:
        if eh_disciplina(content[i]):
            codigo, nome = parse_disciplina(content[i])
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
            while i < num_lines:
                if not eh_nova_turma(content[i]):
                    break

                (t, descricao, vagas, turno,
                 aula, professor, reserva, obs) = parse_turma(content[i])
                turmas[t] = {'descrição': descricao, 'vagas': vagas,
                             'turno': turno, 'aulas': aula,
                             'professores': professor,
                             'reserva': reserva, 'observação': obs}

                i += 1
                while i < num_lines:
                    if eh_nova_turma(content[i]) or eh_disciplina(content[i]):
                        break

                    (_, descricao, vagas, turno,
                     aula, professor, reserva, obs) = parse_turma(content[i])

                    if descricao:
                        turmas[t]['descrição'] += ' ' + descricao
                    if aula:
                        turmas[t]['aulas'].update(aula)
                    if professor:
                        turmas[t]['professores'] += ', ' + professor
                    if reserva:
                        turmas[t]['reserva'] += ' ' + reserva
                    if obs:
                        turmas[t]['observação'] += ' ' + obs

                    i += 1

            oferta[codigo]['turmas'] = turmas
            # ### Turmas ###

    print('{} disciplinas.'.format(len(oferta)))
    return oferta
