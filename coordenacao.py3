#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


from SIGRA.Acompanhamento import Alunos
from SIGRA.Planejamento import Curso
from SIGRA.Planejamento import Fluxo
from SIGRA.Planejamento import Oferta


def arquivo_de_emails(arquivo, encoding='ISO-8859-1',
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
        f.write('Ano;' + ';'.join(col_names) + '\n')

        for periodo in sorted(stats.keys()):
            f.write(periodo)
            for k in col_names:
                t = stats[periodo][k]['Mas'] + stats[periodo][k]['Fem']
                f.write(';' + str(t))
            f.write('\n')


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


if __name__ == '__main__':
    # arquivo_de_emails(arquivo='relatorios/Acompanhamento/Alunos/ALUTEL/2017-2.txt')

    # csv_com_entrada_saida_de_alunos('relatorios/Planejamento/Curso/CUREGEP/' + f for f in ['1997.txt', '1998.txt', '2000.txt', '2002.txt', '2004.txt', '2006.txt', '2008.txt', '2010.txt', '2012.txt', '2014.txt', '2016.txt'])

    # print(turmas_ofertadas(['guilherme novaes'], 'relatorios/Planejamento/Oferta/OFELST/2018-1.txt'))

    # pretty_fluxo('relatorios/Planejamento/Fluxo/FLULST/6912.txt', 'utf-16')

    oferta_obrigatorias('relatorios/Planejamento/Oferta/OFELST/2018-1.txt', 'utf-16', 'relatorios/Planejamento/Fluxo/FLULST/6912.txt', 'utf-16', 'mecat')

    pass
