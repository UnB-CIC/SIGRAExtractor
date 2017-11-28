#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


import re

from SIGRA.Acompanhamento import Alunos
from SIGRA.Acompanhamento import HistoricoEscolar
from SIGRA.Planejamento import Curso
from SIGRA.Planejamento import Disciplina
from SIGRA.Planejamento import Fluxo
from SIGRA.Planejamento import Oferta
from SIGRA import utils


def alunos_matriculados_por_semestre(ALUREL, HEDIS, habilitacoes=[]):
    '''Retorna um dicionário indicando, para cada período letivo em que uma
    disciplina foi oferecida, quantos alunos de determinadas habilitações foram
    matriculados.

    Argumentos:
    ALUREL -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              ser o relatório exportado via:
              SIGRA > Acompanhamento > Alunos > ALUREL
    HEDIS -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
             relatório exportado via:
             SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                    todas.
                    (default [])
    '''
    alunos = Alunos.Relacao(ALUREL)

    if not habilitacoes:
        matriculas = set(m for infos in alunos.values()
                         for periodo in infos['Alunos'].values()
                         for m in periodo)
    else:
        matriculas = set(m for habilitacao in habilitacoes
                         for periodo in alunos[habilitacao]['Alunos'].values()
                         for m in periodo)

    matriculados = HistoricoEscolar.AlunosQueCursaramDisciplina(HEDIS)

    contador = {}
    for periodo in matriculados:
        contador[periodo] = sum(1 for turma in matriculados[periodo]
                                for m in matriculados[periodo][turma]
                                if m in matriculas)
    return contador


def arquivo_de_emails(ALUTEL, contact='{nome} <{email}>',
                      out_file='emails.txt'):
    '''Gera um arquivo com a lista de e-mails dos alunos regulares de um curso.

    Argumentos:
    ALUTEL -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              relatório exportado via:
              SIGRA > Acompanhamento > Alunos > ALUTEL
    contact -- formatação de cada registro
               (default nome <email>)
    out_file -- arquivo onde gravas a lista de e-mails.
    '''
    relacao = Alunos.Contatos(ALUTEL)
    emails = [contact.format(nome=info['nome'], email=info['e-mail'],
                             telefone=info['telefone'])
              for info in relacao.values()]

    with open(out_file, 'w') as f:
        f.write('\n'.join(email for email in sorted(emails)))


def csv_com_entrada_saida_de_alunos(CUREGEPs, out_file='stats.csv'):
    '''Gera um arquivo com a as informações de entrada/saída de alunos do curso
    por semestre.

    Argumentos:
    CUREGEPs -- lista com os caminhos para os arquivos (UTF-16) contendo os
                dados, que devem ser o relatório exportado via:
                SIGRA > Planejamento > Curso > CUREGEP
    out_file -- arquivo onde gravar os dados.
    '''
    stats = Curso.Estatisticas(CUREGEPs)
    col_names = sorted(next(iter(stats.values())).keys())

    with open(out_file, 'w') as f:
        f.write(';'.join(['Ano'] + col_names) + '\n')

        for periodo in sorted(stats.keys()):
            f.write(periodo)
            for k in col_names:
                t = stats[periodo][k]['Mas'] + stats[periodo][k]['Fem']
                f.write(';' + str(t))
            f.write('\n')


def estatistica_docente_por_semestre(HEMEN, OFELST, ignore=[]):
    '''Cruza as informações do histórico de menções de um semestre com a lista
    de oferta, retornando um dicionário com a informações.

    Argumentos:
    HEMEN -- caminho para o arquivo (UTF-16) contendo os dados das menções, que
             deve ser o relatório exportado via:
             SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da oferta, que
              deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    ignore -- lista com código de disciplinas que devem ser ignoradas na
              contabilização (como '167681' -> Trabalho de Graduação 1).
    '''
    estatisticas_de_mencoes = HistoricoEscolar.EstatisticaDeMencoes(HEMEN)
    oferta = Oferta.Listagem(OFELST)

    estatisticas = {}
    for periodo in estatisticas_de_mencoes:
        docentes = {}
        for stats in estatisticas_de_mencoes[periodo].values():
            for codigo in stats:
                if codigo in ignore:
                    continue
                if '' in stats[codigo]['Turmas']:
                    del stats[codigo]['Turmas']['']
                for turma in stats[codigo]['Turmas']:
                    if stats[codigo]['Turmas'][turma] == 0:
                        continue
                    if codigo in oferta:
                        creds = utils.str2creditos(oferta[codigo]['créditos'])
                        num_cred = sum(v for v in creds.values()) - creds['Estudo']

                        if turma in oferta[codigo]['turmas']:
                            num_alunos = stats[codigo]['Turmas'][turma]
                            professores = oferta[codigo]['turmas'][turma]['professores'].split(',')
                            for p in professores:
                                p = p.strip()
                                if p not in docentes:
                                    docentes[p] = {'creditos': 0,
                                                   'turmas': 0,
                                                   'alunos': 0}
                                docentes[p]['creditos'] += num_cred / len(professores)
                                docentes[p]['turmas'] += 1
                                docentes[p]['alunos'] += num_alunos
        estatisticas[periodo] = docentes
    return estatisticas

def media_de_alunos_matriculados_por_semestre(lista_de_semestres,
                                              ignora_verao=True,
                                              filtro_de_semestre=''):
    '''Retorna a média de alunos matriculados por semestre.

    Argumentos:
    lista_de_semestres -- lista de semestres letivos a serem considerados.
    ignora_verao -- indica se deve ou não ignorar semestre de verão
                    (default True)
    filtro_de_semestre -- filtro de semestres a serem considerados. Por
                          exemplo, o filtro para considerar apenas períodos
                          entre 2014/2 e 2016/2 seria
                          '2014/2 <= {periodo} <= 2016/2'
                          (default '')
    '''
    def entre_aspas(matchobj):
        return '\'{}\''.format(matchobj.group(0))

    def filtra(p):
        f = re.sub(r'\d{4}/\d', entre_aspas,
                   filtro_de_semestre.format(periodo))
        return not eval(f)

    n = 0
    total = 0
    for periodo, matriculados in lista_de_semestres.items():
        if (matriculados > 0):
            if ignora_verao and periodo.endswith('/0'):
                continue
            if filtro_de_semestre and filtra(periodo):
                continue
            total += matriculados
            n += 1
    return total / n if n else 0


def oferta_obrigatorias(OFELST, FLULST, habilitacao='', mostra_opcoes=False):
    '''Imprime o fluxo de uma habilitação, indicando a oferta de disciplinas
    obrigatórias.

    Argumentos:
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Lista de
              Oferta, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    FLULST -- caminho para o arquivo (UTF-16) contendo os dados do Fluxo de um
              curso, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    habilitacao -- parte do nome da habilitação para qual se quer filtrar as
                   turmas reservadas
                   (default '')
    mostra_opcoes -- define se deve mostrar opções de horários para a
                     disciplina ou não
                     (default False)
    '''
    DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

    oferta = Oferta.Listagem(OFELST)
    fluxo = Fluxo.Listagem(FLULST)

    for disciplinas in fluxo.values():
        if 'OPT' in disciplinas:
            del disciplinas['OPT']

    for p in fluxo:
        print('\n\nPeríodo: ', p)
        print('===========')

        for disciplinas in fluxo[p].values():
            for codigo in sorted(disciplinas):
                turmas = sorted(t for t in oferta[codigo]['turmas']
                                for r in oferta[codigo]['turmas'][t]['reserva']
                                if habilitacao in r.lower())

                print('\n', codigo, oferta[codigo]['nome'])
                if habilitacao:
                    print('\tReserva')
                for t in turmas:
                    turma = oferta[codigo]['turmas'][t]
                    for dia in DIAS:
                        for aula in turma['aulas']:
                            if dia in aula:
                                hora = aula[dia]['horário']
                                print('\t\t', t, dia, hora)
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


def pretty_fluxo(FLULST):
    '''Imprime o fluxo de uma habilitação.

    Argumentos:
    FLULST -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    '''
    fluxo = Fluxo.Listagem(FLULST)

    print()
    for p, periodo in fluxo.items():
        num_cred = 0
        for disciplinas in periodo.values():
            for d in disciplinas.values():
                creds = utils.str2creditos(d['créditos'])
                num_cred += sum(v for v in creds.values()) - creds['Estudo']
        print('{} - ({} créditos)'.format(p, num_cred))

        for tipo, disciplinas in sorted(periodo.items()):
            for codigo, detalhes in sorted(disciplinas.items()):
                print(tipo, codigo, detalhes['nome'])

        print()


def pretty_grade(OFELST, FLULST, habilitacao='', filtro_tipo=[]):
    '''Imprime o fluxo de uma habilitação, em grade para facilitar a
    visualização, indicando a oferta de disciplinas obrigatórias.

    Argumentos:
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    FLULST -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    habilitacao -- parte do nome da habilitação para qual se quer filtrar as
                   turmas reservadas.
                   (default '')
    filtro_tipo -- lista com os tipos de disciplinas a serem filtradas. Por
                   exemplo, para remover as optativas basta incluir o elemento
                   'OPT' a lista. Outras opções são 'OBR', 'OBS', 'ML', etc.
                   (default [])
    '''
    DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']
    HORARIOS = ['{:02d}:00 {:02d}:50'.format(h, h + 1)
                for h in range(8, 19, 2)]

    oferta = Oferta.Listagem(OFELST)

    fluxo = Fluxo.Listagem(FLULST)
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
                        turmas = [turma for turma, detalhes in turmas.items()
                                  for reserva in detalhes['reserva']
                                  if habilitacao in reserva.lower()]

                        for t in sorted(turmas):
                            turma = oferta[codigo]['turmas'][t]
                            for aula in turma['aulas']:
                                if dia in aula and aula[dia]['horário'] == h:
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
                for cell in row:
                    print('{0: <12}'.format(cell), end='')
                print()


def turmas_ofertadas(professores, OFELST):
    ''' Dada uma lista de nomes de professores, retorna um dicionário contendo
    as turmas a serem ofertadas por cada professor(a).

    Argumentos:
    professores -- lista de nomes [parciais] professores.
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser o
              relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    '''
    oferta = Oferta.Listagem(OFELST)
    oferta_prof = {}

    for professor in professores:
        for codigo, disciplina in sorted(oferta.items()):
            for turma, dados in disciplina['turmas'].items():
                if professor.lower() in dados['professores'].lower():
                    if professor not in oferta_prof:
                        oferta_prof[professor] = {}
                    if codigo not in oferta_prof[professor]:
                        oferta_prof[professor][codigo] = {}
                    oferta_prof[professor][codigo][turma] = dados

    return oferta_prof


CAMINHO = 'relatorios'


def acom(arquivo):
    return '/'.join([CAMINHO, 'Acompanhamento', arquivo])


def plan(arquivo):
    return '/'.join([CAMINHO, 'Planejamento', arquivo])


if __name__ == '__main__':
    # arquivo_de_emails(acom('Alunos/ALUTEL/2017-2.txt'))

    # curegeps = [plan('Curso/CUREGEP/' + f) for f in ['1997.txt', '1998.txt',
    #                                                  '2000.txt', '2002.txt',
    #                                                  '2004.txt', '2006.txt',
    #                                                  '2008.txt', '2010.txt',
    #                                                  '2012.txt', '2014.txt',
    #                                                  '2016.txt']]
    # csv_com_entrada_saida_de_alunos(curegeps)

    # print(turmas_ofertadas(['guilherme novaes'],
    #                        plan('Oferta/OFELST/2018-1.txt')))

    # pretty_fluxo(plan('Fluxo/FLULST/6912.txt'))

    # oferta_obrigatorias(plan('Oferta/OFELST/2018-1.txt'),
    #                     plan('Fluxo/FLULST/6912.txt'), 'mecat')
    # pretty_grade(plan('Oferta/OFELST/2018-1.txt'),
    #              plan('Fluxo/FLULST/6912.txt'), 'mecat', ['OPT'])

    # FIS3 = 'HistoricoEscolar/HEDIS/IFD/118044_2017-2.txt'
    # lista = alunos_matriculados_por_semestre(acom('Alunos/ALUREL/949.txt'),
    #                                          acom(FIS3))
    # print(lista)

    # filtro = '2014/2 <= {} <= 2017/2'
    # print(media_de_alunos_matriculados_por_semestre(lista, True, filtro))

    # disciplinas = Disciplina.Listagem(plan('Disciplina/DISLST/2017-2.txt'))
    # print(disciplinas['113476'])

    # periodos = ['2015-1', '2015-2', '2016-1', '2016-2', '2017-1']
    # oferta = {}
    # for p in periodos:
    #     oferta[p] = Oferta.Listagem(plan('Oferta/OFELST/116/{}.txt'.format(p)))
    # print(oferta)

    LIC = ['116891', '116904', '116840']
    BCC = ['116912', '116921', '116475']
    EC = ['207322', '207331']
    EM = ['167681', '167665']
    tccs = LIC + BCC + EC + EM
    estudos_em = ['116556', '116521', '116661', '116629', '116734']
    topicos_em = ['116297']
    estagio = ['207314', '207438', '117340']
    ignore = tccs + estudos_em + topicos_em + estagio

    HEMEN = acom('HistoricoEscolar/HEMEN/2015-1/116.txt')
    OFELST = plan('Oferta/OFELST/116/2015-1.txt')
    stats = estatistica_docente_por_semestre(HEMEN, OFELST, ignore)
    i = 1
    for p, profs in stats.items():
        print(p)
        for p in sorted(profs):
            print(i, p, profs[p]['creditos'])
            i += 1
        print('Media de créditos/professor', sum(p['creditos'] for p in profs.values())/len(profs))
        print('Media de alunos/turma', sum(p['alunos'] for p in profs.values())/sum(p['turmas'] for p in profs.values()))
