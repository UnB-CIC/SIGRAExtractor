#  -*- coding: utf-8 -*-
#    @package: professores.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções para lidar com informações dos professores.


from sigra.acompanhamento import historico_escolar as ac_he
from sigra.planejamento import oferta as pl_oferta


def carga_horaria_ofertada(OFELST):
    '''Retorna um dicionário contendo a carga horária a ser cumprida por cada
    professor(a), considerando disciplinas ofertadas com pelo menos 1 vaga.

    Argumentos:
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Oferta,
              que deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    '''
    oferta = pl_oferta.listagem(OFELST)

    carga = {}
    for codigo, disciplina in oferta.items():
        for turma, detalhes in disciplina.turmas.items():
            if int(detalhes.vagas) > 0:
                for professor in detalhes.professores:
                    if professor not in carga:
                        carga[professor] = 0
                    carga[professor] += disciplina.creditos.total()

    return carga


def estatistica_por_semestre(HEEME,
                             OFELST,
                             ignore=[]):
    '''Cruza as informações do histórico de menções de um semestre com a
    lista de oferta, retornando um dicionário com a informações.

    Argumentos:
    HEEME -- caminho para o arquivo (UTF-16) contendo o histórico de
             menções, que deve ser o relatório exportado via:
             SIGRA > Acompanhamento > Histórico Escolar > HEEME
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da oferta,
              que deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
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

                    num_cred = oferta[codigo].creditos.total()

                    if turma in oferta[codigo].turmas:
                        num_alunos = disciplinas[codigo]['Turmas'][turma]
                        num_professores = len(oferta[codigo].turmas[
                                              turma].professores)
                        for p in oferta[codigo].turmas[turma].professores:
                            if p not in docentes:
                                docentes[p] = {'creditos': 0,
                                               'turmas': 0,
                                               'alunos': 0}
                            docentes[p]['creditos'] += (num_cred /
                                                        num_professores)
                            docentes[p]['turmas'] += 1
                            docentes[p]['alunos'] += num_alunos
        estatisticas[periodo] = docentes
    return estatisticas


def turmas_ofertadas(professores,
                     OFELST):
    ''' Dada uma lista de nomes de professores, retorna um dicionário
    contendo as turmas a serem ofertadas por cada professor(a).

    Argumentos:
    professores -- lista de nomes [parciais] professores.
    OFELST -- caminho para o arquivo (UTF-16) contendo os dados da Oferta,
              que deve ser o relatório exportado via:
              SIGRA > Planejamento > Oferta > OFELST
    '''
    oferta = pl_oferta.listagem(OFELST)

    oferta_docente = {}
    for codigo, disciplina in oferta.items():
        for turma, detalhes in disciplina.turmas.items():
            if professores:
                current_professores = [p for p in professores
                                       if p.lower() in (prof.lower()
                                                        for prof in
                                                        detalhes.professores)]
            else:
                current_professores = detalhes.professores

            for professor in current_professores:
                if professor not in oferta_docente:
                    oferta_docente[professor] = {}
                if codigo not in oferta_docente[professor]:
                    oferta_docente[professor][codigo] = {}
                oferta_docente[professor][codigo][turma] = detalhes

    return oferta_docente
