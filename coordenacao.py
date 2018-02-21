#  -*- coding: utf-8 -*-
#    @package: coordenacao.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.

import re

from sigra import utils
from sigra.acompanhamento import alunos as ac_alunos
from sigra.acompanhamento import historico_escolar as ac_he
from sigra.planejamento import curso as pl_curso
from sigra.planejamento import fluxo as pl_fluxo
from sigra.planejamento import oferta as pl_oferta


class Discentes():
    @staticmethod
    def resultado_matriculados_por_semestre(ALUREL,
                                            HEDIS,
                                            habilitacoes=[]):
        '''Retorna um dicionário indicando, para cada período letivo em que uma
        disciplina foi oferecida, quais alunos de determinadas habilitações
        foram matriculados e seus respectivos desempenhos no período.

        Argumentos:
        ALUREL -- caminho para o arquivo (UTF-16) contendo a relação de alunos
                  a serem considerados, que deve ser o ser o relatório
                  exportado via:
                  sigra > Acompanhamento > Alunos > ALUREL
        HEDIS -- caminho para o arquivo (UTF-16) contendo o histórico de
                 matrículas da disciplina , que deve ser o relatório exportado
                 via:
                 sigra > Acompanhamento > Histórico Escolar > HEDIS
        habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                        todas.
                        (default [])
        '''
        alunos = ac_alunos.relacao(ALUREL)
        cursaram = ac_he.alunos_que_cursaram_disciplina(HEDIS)

        if not habilitacoes:
            habilitacoes = alunos.keys()

        matriculas = set(matricula for habilitacao in habilitacoes
                         for periodo in alunos[habilitacao]['Alunos'].values()
                         for matricula in periodo)

        for periodo in cursaram:
            for turma in cursaram[periodo].values():
                alunos_de_outras_habilitacoes = set(turma.keys()) - matriculas
                for matricula in alunos_de_outras_habilitacoes:
                    del turma[matricula]
        return cursaram

    @staticmethod
    def matriculados_por_semestre(ALUREL,
                                  HEDIS,
                                  habilitacoes=[]):
        '''Retorna um dicionário indicando, para cada período letivo em que uma
        disciplina foi oferecida, quantos alunos de determinadas habilitações
        foram matriculados.

        Argumentos:
        ALUREL -- caminho para o arquivo (UTF-16) contendo a relação de alunos
                  a serem considerados, que deve ser o ser o relatório
                  exportado via:
                  sigra > Acompanhamento > Alunos > ALUREL
        HEDIS -- caminho para o arquivo (UTF-16) contendo o histórico de
                 matrículas da disciplina , que deve ser o relatório exportado
                 via:
                 sigra > Acompanhamento > Histórico Escolar > HEDIS
        habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                        todas.
                        (default [])
        '''
        cursaram = Discentes.resultado_matriculados_por_semestre(ALUREL,
                                                                 HEDIS,
                                                                 habilitacoes)

        import collections
        contador = collections.defaultdict(int)
        for periodo in cursaram:
            for turma in cursaram[periodo].values():
                for matricula in turma:
                    contador[periodo] += 1

        return contador

    @staticmethod
    def media_de_matriculados_por_semestre(matriculados_por_semestre,
                                           ignora_verao=True,
                                           filtro_de_semestre=None):
        '''Retorna a média de alunos matriculados por semestre.

        Argumentos:
        matriculados_por_semestre -- dicionário de semestres letivos: alunos
                                     matriculados a serem considerados (veja o
                                     método
                                     Discentes.matriculados_por_semestre).
        ignora_verao -- indica se deve ou não ignorar semestre de verão
                        (default True)
        filtro_de_semestre -- filtro de semestres a serem considerados. Por
                              exemplo, o filtro para considerar apenas períodos
                              entre 2014/2 (inclusive) e 2016/2 (exclusive)
                              seria '2014/2 <= {periodo} < 2016/2'
                              (default None)
        '''
        def entre_aspas(matchobj):
            return '\'{}\''.format(matchobj.group(0))

        def filtra(p):
            f = re.sub(r'\d{4}/\d', entre_aspas,
                       filtro_de_semestre.format(periodo))
            return not eval(f)

        num_turmas = 0
        total_matriculados = 0
        for periodo, matriculados in matriculados_por_semestre.items():
            if matriculados < 1:
                continue
            if ignora_verao and periodo.endswith('/0'):
                continue
            if filtro_de_semestre and filtra(periodo):
                continue
            total_matriculados += matriculados
            num_turmas += 1
        return total_matriculados / num_turmas if num_turmas else 0

    @staticmethod
    def contatos(ALUTEL,
                 formato='{nome} <{email}>',
                 arquivo='emails.txt'):
        '''Gera um arquivo com a lista de e-mails dos alunos regulares de um
        curso.

        Argumentos:
        ALUTEL -- caminho para o arquivo (UTF-16) contendo a listagem das
                  informações de contatos dos alunos, que deve ser o relatório
                  exportado via:
                  sigra > Acompanhamento > Alunos > ALUTEL
        formato -- formatação de cada registro.
                   (default nome <email>)
        arquivo -- arquivo onde gravar a lista de e-mails.
        '''
        relacao = ac_alunos.contatos(ALUTEL)
        return [formato.format(nome=info['nome'],
                               email=info['e-mail'],
                               telefone=info['telefone'])
                for info in relacao.values()]

    @staticmethod
    def csv_com_entrada_saida_de_alunos(CUREGEPs, arquivo='alunos.csv',
                                        separador=';'):
        '''Gera um arquivo com a as informações de entrada/saída de alunos do
        curso por semestre, como uma listagem CSV.

        Argumentos:
        CUREGEPs -- lista com os caminhos para os arquivos (UTF-16) contendo os
                    as informações sobre o curso, que devem ser o relatório
                    exportado via:
                    sigra > Planejamento > Curso > CUREGEP
        arquivo -- caminho para o arquivo onde gravar os dados.
                   (default alunos.csv)
        separador -- separador de valores.
                     (default ;)
        '''
        estatisticas = pl_curso.estatisticas(CUREGEPs)
        col_names = sorted(next(iter(estatisticas.values())).keys())

        with open(arquivo, 'w') as f:
            f.write('{}\n'.format(separador.join(['Período'] + col_names)))

            for periodo in sorted(estatisticas.keys()):
                f.write(periodo)
                for k in col_names:
                    estatistica = estatisticas[periodo][k].values()
                    total = sum(int(n) for n in estatistica)
                    f.write('{}{}'.format(separador, total))
                f.write('\n')


class Docente():
    def estatistica_por_semestre(HEEME,
                                 OFELST,
                                 ignore=[]):
        '''Cruza as informações do histórico de menções de um semestre com a
        lista de oferta, retornando um dicionário com a informações.

        Argumentos:
        HEEME -- caminho para o arquivo (UTF-16) contendo o histórico de
                 menções, que deve ser o relatório exportado via:
                 sigra > Acompanhamento > Histórico Escolar > HEEME
        OFELST -- caminho para o arquivo (UTF-16) contendo os dados da oferta,
                  que deve ser o relatório exportado via:
                  sigra > Planejamento > Oferta > OFELST
        ignore -- lista com código de disciplinas que devem ser ignoradas na
                  contabilização (como '167681' -> Trabalho de Graduação 1).
        '''
        estatisticas_de_mencoes = ac_he.estatisticas_de_mencoes(HEEME)
        oferta = pl_oferta.listagem(OFELST)

        estatisticas = {}
        for periodo in estatisticas_de_mencoes:
            docentes = {}
            for disciplinas in estatisticas_de_mencoes[periodo].values():
                for codigo in disciplinas:
                    if disciplinas[codigo]['Nível'] != 'GR':
                        continue
                    if codigo in ignore or codigo not in oferta:
                        continue

                    for turma in disciplinas[codigo]['Turmas']:
                        if (not turma or
                                disciplinas[codigo]['Turmas'][turma] == 0):
                            continue

                        num_cred = utils.Creditos.total(oferta[codigo][
                                                        'créditos'])

                        if turma in oferta[codigo]['turmas']:
                            num_alunos = disciplinas[codigo]['Turmas'][turma]
                            professores = oferta[codigo]['turmas'][turma][
                                'professores'].split(',')
                            for p in professores:
                                if p not in docentes:
                                    docentes[p] = {'creditos': 0,
                                                   'turmas': 0,
                                                   'alunos': 0}
                                docentes[p]['creditos'] += (num_cred /
                                                            len(professores))
                                docentes[p]['turmas'] += 1
                                docentes[p]['alunos'] += num_alunos
            estatisticas[periodo] = docentes
        return estatisticas

    @staticmethod
    def turmas_ofertadas(professores,
                         OFELST):
        ''' Dada uma lista de nomes de professores, retorna um dicionário
        contendo as turmas a serem ofertadas por cada professor(a).

        Argumentos:
        professores -- lista de nomes [parciais] professores.
        OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Oferta,
                  que deve ser o relatório exportado via:
                  sigra > Planejamento > Oferta > OFELST
        '''
        oferta = pl_oferta.listagem(OFELST)
        oferta_docente = {}

        for professor in professores:
            for codigo, disciplina in sorted(oferta.items()):
                for turma, dados in disciplina['turmas'].items():
                    if professor.lower() in dados['professores'].lower():
                        if professor not in oferta_docente:
                            oferta_docente[professor] = {}
                        if codigo not in oferta_docente[professor]:
                            oferta_docente[professor][codigo] = {}
                        oferta_docente[professor][codigo][turma] = dados

        return oferta_docente


class Terminal():
    @staticmethod
    def fluxo(FLULST):
        '''Imprime o fluxo de uma habilitação, de maneira formatada, no
        terminal.

        Argumentos:
        FLULST -- caminho para o arquivo (UTF-16) contendo a listagem do fluxo
                  de uma habilitação, que deve ser o relatório exportado via:
                  sigra > Planejamento > Fluxo > FLULST
        '''
        fluxo = pl_fluxo.listagem(FLULST)

        print()
        for p, periodo in fluxo.items():
            num_cred = sum(utils.Creditos.total(d['créditos'])
                           for disciplinas in periodo.values()
                           for d in disciplinas.values())
            print('{} - ({} créditos)'.format(p, num_cred))

            for tipo, disciplinas in sorted(periodo.items()):
                for codigo, detalhes in sorted(disciplinas.items()):
                    print(tipo, codigo, detalhes['nome'])

            print()

    def grade(OFELST, FLULST, habilitacao='', filtro_tipo=[]):
        '''Imprime o fluxo de uma habilitação, de maneira formatada em grade no
        terminal para facilitar a visualização, indicando a oferta de
        disciplinas obrigatórias.

        Argumentos:
        OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Oferta,
                  que deve ser o relatório exportado via:
                  sigra > Planejamento > Fluxo > FLULST
        FLULST -- caminho para o arquivo (UTF-16) contendo os dados do Fluxo de
                  uma habilitação, que deve ser o relatório exportado via:
                  sigra > Planejamento > Fluxo > FLULST
        habilitacao -- parte do nome da habilitação para qual se quer filtrar
                       as turmas reservadas.
                       (default '')
        filtro_tipo -- lista com os tipos de disciplinas a serem filtradas. Por
                       exemplo, para remover as optativas basta incluir o
                       elemento 'OPT' a lista. Outras opções são 'OBR', 'OBS',
                       'ML', etc.
                       (default [])
        '''
        DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
        HORARIOS = ['{:02d}:00 {:02d}:50'.format(h, h + 1)
                    for h in range(8, 19, 2)]

        oferta = pl_oferta.listagem(OFELST)

        fluxo = pl_fluxo.listagem(FLULST)
        for tipo in filtro_tipo:
            for disciplinas in fluxo.values():
                if tipo in disciplinas:
                    del disciplinas[tipo]

        for p in fluxo:
            print('\n\nPeríodo: ', p)
            print('===========')

            table_data = [[''] + DIAS]
            for h in HORARIOS:
                linha = [h]

                for dia in DIAS:
                    aulas_do_dia = ''
                    for disciplinas in fluxo[p].values():
                        for codigo in disciplinas:
                            if codigo not in oferta:
                                continue
                            turmas = oferta[codigo]['turmas']
                            turmas = [t for t, detalhes in turmas.items()
                                      for reserva in detalhes['reserva']
                                      if habilitacao in reserva.lower()]

                            for t in sorted(turmas):
                                turma = oferta[codigo]['turmas'][t]
                                for aula in turma['aulas']:
                                    if (dia in aula and
                                            aula[dia]['horário'] == h):
                                        if aulas_do_dia:
                                            aulas_do_dia += ' '
                                        aulas_do_dia += codigo + ' ' + t
                    linha.append(aulas_do_dia)
                table_data.append(linha)

            try:
                from terminaltables import AsciiTable
                print(AsciiTable(table_data).table)
            except Exception:
                for row in table_data:
                    print(''.join('{0: <12}'.format(cell) for cell in row))

    @staticmethod
    def oferta_obrigatorias(OFELST,
                            FLULST,
                            habilitacao='',
                            mostra_opcoes=False):
        '''Imprime o fluxo de uma habilitação, indicando a oferta de disciplinas
        obrigatórias.

        Argumentos:
        OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Lista de
                  Oferta, que deve ser o relatório exportado via:
                  sigra > Planejamento > Oferta > OFELST
        FLULST -- caminho para o arquivo (UTF-16) contendo os dados do Fluxo de
                  um curso, que deve ser o relatório exportado via:
                  sigra > Planejamento > Fluxo > FLULST
        habilitacao -- parte do nome da habilitação para qual se quer filtrar
                       as turmas reservadas
                       (default '')
        mostra_opcoes -- define se deve mostrar opções de horários para a
                         disciplina ou não
                         (default False)
        '''
        oferta = pl_oferta.listagem(OFELST)
        fluxo = pl_fluxo.listagem(FLULST)

        for disciplinas in fluxo.values():
            if 'OPT' in disciplinas:
                del disciplinas['OPT']

        DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

        for p in fluxo:
            print('\n\nPeríodo: ', p)
            print('===========')

            for disciplinas in fluxo[p].values():
                for codigo in sorted(disciplinas):
                    turmas = sorted(t for t in oferta[codigo]['turmas']
                                    for r in oferta[codigo]['turmas'][t][
                                        'reserva']
                                    if habilitacao in r.lower())

                    print('\n', codigo, oferta[codigo]['nome'])

                    reservas = []
                    for t in turmas:
                        turma = oferta[codigo]['turmas'][t]
                        for dia in DIAS:
                            for aula in turma['aulas']:
                                if dia in aula:
                                    hora = aula[dia]['horário']
                                    reservas.append('\t\t{} {} {}'.format(
                                                    t, dia, hora))
                    if habilitacao and reservas:
                        print('\tReserva')
                        print('\n'.join(reservas))

                    if mostra_opcoes:
                        if habilitacao:
                            print('\tOutros')
                        for t in sorted(oferta[codigo]['turmas']):
                            if t not in turmas:
                                turma = oferta[codigo]['turmas'][t]
                                for dia in DIAS:
                                    if dia in turma['aulas']:
                                        hora = turma['aulas'][dia]['horário']
                                        print('\t\t', t, dia, hora)
