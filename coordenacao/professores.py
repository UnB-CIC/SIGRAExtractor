#  -*- coding: utf-8 -*-
#    @package: professores.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções para lidar com informações dos professores.


from sigra import utils
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
    for codigo, dados in oferta.items():
        for turma, detalhes in dados['turmas'].items():
            if int(detalhes['vagas']) > 0:
                for professor in detalhes['professores'].split(','):
                    professor = professor.strip()
                    if professor not in carga:
                        carga[professor] = 0
                    carga[professor] += utils.Creditos.total(dados['créditos'])

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

    oferta_docente = {professor: {codigo: {turma: dados}}
                      for codigo, disciplina in oferta.items()
                      for turma, dados in disciplina['turmas'].items()
                      for professor in professores
                      if professor.lower() in dados['professores'].lower()}

    return oferta_docente