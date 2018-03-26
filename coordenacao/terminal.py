#  -*- coding: utf-8 -*-
#    @package: terminal.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções para mostrar informações no terminal.


from sigra.planejamento import fluxo as pl_fluxo
from sigra.planejamento import oferta as pl_oferta


def fluxo(FLULST):
    '''Imprime o fluxo de uma habilitação, de maneira formatada, no
    terminal.

    Argumentos:
    FLULST -- caminho para o arquivo (UTF-16) contendo a listagem do fluxo
              de uma habilitação, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    '''
    fluxo = pl_fluxo.listagem(FLULST)

    print()
    for periodo in sorted(fluxo):
        print('{}\n'.format(fluxo[periodo]))


def grade(OFELST, FLULST, habilitacao='', filtro_tipo=[]):
    '''Imprime o fluxo de uma habilitação, de maneira formatada em grade no
    terminal para facilitar a visualização, indicando a oferta de
    disciplinas obrigatórias.

    Argumentos:
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Oferta,
              que deve ser o relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    FLULST -- caminho para o arquivo (UTF-16) contendo os dados do Fluxo de
              uma habilitação, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    habilitacao -- parte do nome da habilitação para qual se quer filtrar
                   as turmas reservadas.
                   (default '')
    filtro_tipo -- lista com os tipos de disciplinas a serem filtradas. Por
                   exemplo, para remover as optativas basta incluir o
                   elemento 'OPT' a lista. Outras opções são 'OBR', 'OBS',
                   'ML', etc.
                   (default [])
    '''
    oferta = pl_oferta.listagem(OFELST)

    fluxo = pl_fluxo.listagem(FLULST)
    for tipo in filtro_tipo:
        for disciplinas in fluxo.values():
            if tipo in disciplinas:
                del disciplinas[tipo]

    for p in sorted(fluxo):
        print('\n\nPeríodo: ', p)
        print('===========')

        table_data = [[''] + pl_oferta.Aula.DIAS]
        for h in pl_oferta.Aula.HORARIOS:
            linha = [h]

            for dia in pl_oferta.Aula.DIAS:
                aulas_do_dia = []
                for disciplinas in fluxo[p].disciplinas.values():
                    for codigo in disciplinas:
                        if codigo not in oferta:
                            continue
                        turmas = oferta[codigo].turmas
                        turmas = [t for t, detalhes in turmas.items()
                                  for reserva in detalhes.reserva
                                  if habilitacao in reserva.lower()]

                        for t in sorted(turmas):
                            turma = oferta[codigo].turmas[t]
                            for aula in turma.aulas:
                                if (dia == aula.dia and
                                        h[:2] == aula.horario[:2]):
                                    aulas_do_dia.append(codigo + ' ' + t)

                linha.append(' '.join(a for a in aulas_do_dia))
            table_data.append(linha)

        try:
            from terminaltables import AsciiTable
            print(AsciiTable(table_data).table)
        except Exception:
            for row in table_data:
                print(''.join('{0: <22}'.format(cell) for cell in row))


def oferta_obrigatorias(OFELST,
                        FLULST,
                        habilitacao='',
                        mostra_opcoes=False):
    '''Imprime o fluxo de uma habilitação, indicando a oferta de disciplinas
    obrigatórias.

    Argumentos:
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Lista de
              Oferta, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    FLULST -- caminho para o arquivo (UTF-16) contendo os dados do Fluxo de
              um curso, que deve ser o relatório exportado via:
              SIGRA > Planejamento > Fluxo > FLULST
    habilitacao -- parte do nome da habilitação para qual se quer filtrar
                   as turmas reservadas
                   (default '')
    mostra_opcoes -- define se deve mostrar opções de horários para a
                     disciplina ou não
                     (default False)
    '''
    oferta = pl_oferta.listagem(OFELST)
    fluxo = pl_fluxo.listagem(FLULST)

    for periodo in fluxo.values():
        if 'OPT' in periodo.disciplinas:
            del periodo.disciplinas['OPT']

    for p in sorted(fluxo):
        print('\n\nPeríodo: ', p)
        print('===========')

        for disciplinas in fluxo[p].disciplinas.values():
            for codigo in sorted(disciplinas):
                turmas = sorted(t for t in oferta[codigo].turmas
                                for r in oferta[codigo].turmas[t].reserva
                                if habilitacao in r.lower())

                print('\n', codigo, oferta[codigo].nome)

                reservas = []
                for t in turmas:
                    turma = oferta[codigo].turmas[t]
                    for dia in pl_oferta.Aula.DIAS:
                        for aula in turma.aulas:
                            if dia == aula.dia:
                                reservas.append('\t\t{} {} {}'.format(
                                                t, dia, aula.horario))
                if habilitacao and reservas:
                    print('\tReserva')
                    print('\n'.join(reservas))

                if mostra_opcoes:
                    if habilitacao:
                        print('\tOutros')
                    for t in sorted(oferta[codigo].turmas):
                        if t not in turmas:
                            turma = oferta[codigo].turmas[t]
                            for dia in pl_oferta.Aula.DIAS:
                                for aula in turma.aulas:
                                    if dia == aula.dia:
                                        print('\t\t', t, dia, aula.horario)
