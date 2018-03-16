#  -*- coding: utf-8 -*-
#    @package: alunos.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções para lidar com informações dos alunos.

import re

from sigra.acompanhamento import alunos as ac_alunos
from sigra.acompanhamento import historico_escolar as ac_he
from sigra.planejamento import curso as pl_curso


def contatos(ALUTEL,
             formato='{nome} <{email}>'):
    '''Gera um arquivo com a lista de e-mails dos alunos regulares de um
    curso.

    Argumentos:
    ALUTEL -- caminho para o arquivo (UTF-16) contendo a listagem das
              informações de contatos dos alunos, que deve ser o relatório
              exportado via:
              SIGRA > Acompanhamento > Alunos > ALUTEL
    formato -- formatação de cada registro. Aceitam-se apenas os seguintes
               parâmetros: nome, email, telefone (entre chaves {}).
               (default {nome} <{email}>)
    '''
    relacao = ac_alunos.contatos(ALUTEL)
    return [formato.format(nome=info['nome'],
                           email=info['e-mail'],
                           telefone=info['telefone'])
            for info in relacao.values()]


def csv_com_entrada_saida_de_alunos(CUREGEPs,
                                    arquivo='alunos.csv',
                                    separador=';'):
    '''Gera um arquivo com a as informações de entrada/saída de alunos do
    curso por semestre, como uma listagem CSV.

    Argumentos:
    CUREGEPs -- lista com os caminhos para os arquivos (UTF-16) contendo os
                as informações sobre o curso, que devem ser o relatório
                exportado via:
                SIGRA > Planejamento > Curso > CUREGEP
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
              SIGRA > Acompanhamento > Alunos > ALUREL
    HEDIS -- caminho para o arquivo (UTF-16) contendo o histórico de
             matrículas da disciplina , que deve ser o relatório exportado
             via:
             SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                    todas.
                    (default [])
    '''
    cursaram = resultado_matriculados_por_semestre(ALUREL,
                                                   HEDIS,
                                                   habilitacoes)

    import collections
    contador = collections.defaultdict(int)
    for periodo in cursaram:
        for turma in cursaram[periodo].values():
            for matricula in turma:
                contador[periodo] += 1

    return contador


def media_de_matriculados_por_semestre(matriculados_por_semestre,
                                       ignora_verao=True,
                                       filtro_de_semestre=None):
    '''Retorna a média de alunos matriculados por semestre.

    Argumentos:
    matriculados_por_semestre -- dicionário de semestres letivos: alunos
                                 matriculados a serem considerados (veja o
                                 método
                                 matriculados_por_semestre).
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
        num_matriculas = len(matriculados)
        if num_matriculas < 1:
            continue
        if ignora_verao and periodo.endswith('/0'):
            continue
        if filtro_de_semestre and filtra(periodo):
            continue
        total_matriculados += num_matriculas
        num_turmas += 1
    return total_matriculados / num_turmas if num_turmas else 0


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
              SIGRA > Acompanhamento > Alunos > ALUREL
    HEDIS -- caminho para o arquivo (UTF-16) contendo o histórico de
             matrículas da disciplina , que deve ser o relatório exportado
             via:
             SIGRA > Acompanhamento > Histórico Escolar > HEDIS
    habilitacoes -- conjunto de habilitações de interesse. Deixe vazia para
                    todas.
                    (default [])
    '''
    alunos = ac_alunos.relacao(ALUREL)
    alunos_que_cursaram = ac_he.alunos_que_cursaram_disciplina(HEDIS)

    if not habilitacoes:
        habilitacoes = alunos.keys()

    matriculas = set(matricula
                     for habilitacao in habilitacoes
                     for periodo in alunos[habilitacao]['Alunos'].values()
                     for matricula in periodo)

    listagem = {}
    for periodo, turmas in alunos_que_cursaram.items():
        for matriculados in turmas.values():
            for matricula, infos in matriculados.items():
                if matricula in matriculas:
                    if periodo not in listagem:
                        listagem[periodo] = {}
                    listagem[periodo][matricula] = infos

    return listagem
