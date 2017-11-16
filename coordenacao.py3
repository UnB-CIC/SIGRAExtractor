#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


import re

from SIGRA.Acompanhamento import Alunos
from SIGRA.Acompanhamento import Historico
from SIGRA.Planejamento import Curso
from SIGRA.Planejamento import Fluxo
from SIGRA.Planejamento import Oferta


def alunos_matriculados_por_semestre(arq_alunos, encoding_alunos,
                                     arq_matriculados, encoding_matriculados,
                                     habilitacoes=[]):
    '''Retorna um dicionário indicando, para cada período letivo em que uma
    disciplina foi oferecida, quantos alunos de determinadas habilitações foram
    matriculados.

    Argumentos:
    arq_alunos -- caminho para o arquivo contendo os dados, que deve ser o
                  relatório exportado via:
                  SIGRA > Acompanhamento > Alunos > ALUREL
    encoding_alunos -- a codificação do arquivo de entrada.
                       (default utf-16)
    arq_matriculados -- caminho para o arquivo contendo os dados, que deve ser
                        o relatório exportado via:
                        SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    encoding_matriculados -- a codificação do arquivo de entrada.
                             (default utf-16)
    habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                    todas.
                    (default [])
    '''
    alunos = Alunos.ALUREL(arq_alunos, encoding_alunos)

    if not habilitacoes:
        habilitacoes = alunos.keys()
    matriculas = set(m for habilitacao in habilitacoes
                     for periodo in alunos[habilitacao]['Alunos'].values()
                     for m in periodo)

    matriculados = Historico.HEDIS(arq_matriculados, encoding_matriculados)

    contador = {}
    for periodo in matriculados:
        contador[periodo] = 0

        for turma in matriculados[periodo]:
            for matricula in matriculados[periodo][turma]:
                if matricula in matriculas:
                    contador[periodo] += 1
    return contador


def arquivo_de_emails(arquivo, encoding='utf-16',
                      contact='{nome} <{email}>', out_file='emails.txt'):
    '''Gera um arquivo com a lista de e-mails dos alunos regulares de um curso.

    Argumentos:
    arquivo -- arquivo contendo os dados, que deve ser o relatório exportado
               via: SIGRA > Acompanhamento > Alunos > ALUTEL
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    contact -- formatação de cada registro
               (default nome <email>)
    out_file -- arquivo onde gravas a lista de e-mails.
    '''
    relacao = Alunos.ALUTEL(arquivo, encoding=encoding)
    emails = [contact.format(nome=info['nome'], email=info['e-mail'],
                             telefone=info['telefone'])
              for info in relacao.values()]

    with open(out_file, 'w') as f:
        f.write('\n'.join(email for email in sorted(emails)))


def csv_com_entrada_saida_de_alunos(arquivos, encoding='utf-16',
                                    out_file='stats.csv'):
    '''Gera um arquivo com a as informações de entrada/saída de alunos do curso
    por semestre.

    Argumentos:
    arquivo -- arquivo contendo os dados, que deve ser o relatório exportado
               via: SIGRA > Planejamento > Curso > CUREGEP
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    out_file -- arquivo onde gravar os dados.
    '''
    stats = Curso.CUREGEP(arquivos, encoding=encoding)
    col_names = sorted(next(iter(stats.values())).keys())

    with open(out_file, 'w') as f:
        f.write(';'.join(['Ano'] + col_names) + '\n')

        for periodo in sorted(stats.keys()):
            f.write(periodo)
            for k in col_names:
                t = stats[periodo][k]['Mas'] + stats[periodo][k]['Fem']
                f.write(';' + str(t))
            f.write('\n')


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


def oferta_obrigatorias(arq_oferta, encoding_oferta, arq_fluxo, fluxo_encoding,
                        habilitacao='', mostra_opcoes=False):
    '''Imprime o fluxo de uma habilitação, indicando a oferta de disciplinas
    obrigatórias.

    Argumentos:
    arq_oferta -- caminho para o arquivo contendo os dados, que deve ser o
                  relatório exportado via:
                  SIGRA > Planejamento > Fluxo > FLULST
    encoding_oferta -- a codificação do arquivo de entrada.
                       (default utf-16)
    arq_fluxo -- caminho para o arquivo contendo os dados, que deve ser o
                 relatório exportado via:
                 SIGRA > Planejamento > Fluxo > FLULST
    fluxo_encoding -- a codificação do arquivo de entrada.
                      (default utf-16)
    habilitacao -- parte do nome da habilitação para qual se quer filtrar as
                   turmas reservadas
                   (default '')
    mostra_opcoes -- define se deve mostrar opções de horários para a
                     disciplina ou não
                     (default False)
    '''
    DIAS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado']

    oferta = Oferta.OFELST(arq_oferta, encoding_oferta)

    fluxo = Fluxo.FLULST(arq_fluxo, fluxo_encoding)
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


def pretty_fluxo(arquivo, encoding):
    '''Imprime o fluxo de uma habilitação.

    Argumentos:
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Planejamento > Fluxo > FLULST
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    fluxo = Fluxo.FLULST(arquivo, encoding)

    print()
    for p, periodo in fluxo.items():
        num_cred = 0
        for disciplinas in periodo.values():
            for d in disciplinas.values():
                num_cred += sum(int(c) for c in d['créditos'].split(':')[:-2])
        print('{} - ({} créditos)'.format(p, num_cred))

        for tipo, disciplinas in sorted(periodo.items()):
            for codigo, detalhes in sorted(disciplinas.items()):
                print(tipo, codigo, detalhes['nome'])
        print()


def pretty_grade(arq_oferta, encoding_oferta, arq_fluxo, fluxo_encoding,
                 habilitacao='', filtro_tipo=[]):
    '''Imprime o fluxo de uma habilitação, em grade para facilitar a
    visualização, indicando a oferta de disciplinas obrigatórias.

    Argumentos:
    arq_oferta -- caminho para o arquivo contendo os dados, que deve ser o
                  relatório exportado via:
                  SIGRA > Planejamento > Fluxo > FLULST
    encoding_oferta -- a codificação do arquivo de entrada.
                       (default utf-16)
    arq_fluxo -- caminho para o arquivo contendo os dados, que deve ser o
                 relatório exportado via:
                 SIGRA > Planejamento > Fluxo > FLULST
    fluxo_encoding -- a codificação do arquivo de entrada.
                      (default utf-16)
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

    oferta = Oferta.OFELST(arq_oferta, encoding_oferta)

    fluxo = Fluxo.FLULST(arq_fluxo, fluxo_encoding)
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


def turmas_ofertadas(professores, arquivo, encoding='utf-16'):
    ''' Dada uma lista de nomes de professores, retorna um dicionário contendo
    as turmas a serem ofertadas por cada professor(a).

    Argumentos:
    professores -- lista de nomes [parciais] professores.
    arquivo -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    oferta = Oferta.OFELST(arquivo, encoding)
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


if __name__ == '__main__':
    # arquivo_de_emails(arquivo='relatorios/Acompanhamento/Alunos/ALUTEL/2017-2.txt', encoding='ISO-8859-1')

    # csv_com_entrada_saida_de_alunos('relatorios/Planejamento/Curso/CUREGEP/' + f for f in ['1997.txt', '1998.txt', '2000.txt', '2002.txt', '2004.txt', '2006.txt', '2008.txt', '2010.txt', '2012.txt', '2014.txt', '2016.txt'])

    # print(turmas_ofertadas(['guilherme novaes'], 'relatorios/Planejamento/Oferta/OFELST/2018-1.txt'))

    # pretty_fluxo('relatorios/Planejamento/Fluxo/FLULST/6912.txt', 'utf-16')

    # oferta_obrigatorias('relatorios/Planejamento/Oferta/OFELST/2018-1.txt', 'utf-16', 'relatorios/Planejamento/Fluxo/FLULST/6912.txt', 'utf-16', 'mecat')
    # pretty_grade('relatorios/Planejamento/Oferta/OFELST/2018-1.txt', 'utf-16', 'relatorios/Planejamento/Fluxo/FLULST/6912.txt', 'utf-16', 'mecat', ['OPT'])

    # lista = alunos_matriculados_por_semestre('relatorios/Acompanhamento/Alunos/ALUREL/949.txt', 'utf-16',
    #                                          'relatorios/Acompanhamento/HistoricoEscolar/HEDIS/118044_2017-2.txt', 'utf-16')
    # print(lista)
    # print(media_de_alunos_matriculados_por_semestre(lista, True, '2014/2 <= {} <= 2017/2'))

    pass
