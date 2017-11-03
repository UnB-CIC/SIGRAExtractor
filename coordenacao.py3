#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


from SIGRA.Acompanhamento import Alunos
from SIGRA.Planejamento import Curso
from SIGRA.Planejamento import Oferta


def arquivo_de_emails(in_file, encoding='ISO-8859-1',
                      contact='{nome} <{email}>', out_file='emails.txt'):
    '''Gera um arquivo com a lista de e-mails dos alunos regulares de um curso.

    Argumentos:
    in_file -- arquivo contendo os dados, que deve ser o relatório exportado
               via: SIGRA > Acompanhamento > Alunos > ALUTEL
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    contact -- formatação de cada registro
               (default nome <email>)
    out_file -- arquivo onde gravas a lista de e-mails.
    '''
    relacao = Alunos.ALUTEL(in_file, encoding=encoding)
    emails = [contact.format(nome=info['nome'], email=info['e-mail'],
                             telefone=info['telefone'])
              for info in relacao.values()]

    with open(out_file, 'w') as f:
        f.write('\n'.join(email for email in sorted(emails)))


def csv_com_entrada_saida_de_alunos(in_files, encoding='utf-16',
                                    out_file='stats.csv'):
    '''Gera um arquivo com a as informações de entrada/saída de alunos do curso
    por semestre.

    Argumentos:
    in_file -- arquivo contendo os dados, que deve ser o relatório exportado
               via: SIGRA > Planejamento > Curso > CUREGEP
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    out_file -- arquivo onde gravar os dados.
    '''
    stats = Curso.CUREGEP(in_files, encoding=encoding)
    col_names = sorted(next(iter(stats.values())).keys())

    with open(out_file, 'w') as f:
        f.write('Ano;' + ';'.join(col_names) + '\n')

        for periodo in sorted(stats.keys()):
            f.write(periodo)
            for k in col_names:
                t = stats[periodo][k]['Mas'] + stats[periodo][k]['Fem']
                f.write(';' + str(t))
            f.write('\n')


def turmas_ofertadas(professores, in_file, encoding='utf-16'):
    ''' Dada uma lista de nomes de professores, retorna um dicionário contendo
    as turmas a serem ofertadas por cada professor(a).

    Argumentos:
    professores -- lista de nomes [parciais] professores.
    in_file -- caminho para o arquivo contendo os dados, que deve ser o
               relatório exportado via:
               SIGRA > Planejamento > Oferta > OFELST
    encoding -- a codificação do arquivo de entrada.
               (default utf-16)
    '''
    oferta = Oferta.OFELST(in_file, encoding)
    oferta_prof = {}

    for professor in professores:
        for codigo, disciplina in oferta.items():
            for turma, dados in disciplina['turmas'].items():
                if professor.lower() in dados['professores'].lower():
                    if professor not in oferta_prof:
                        oferta_prof[professor] = {}
                    if codigo not in oferta_prof[professor]:
                        oferta_prof[professor][codigo] = {}
                    oferta_prof[professor][codigo][turma] = dados

    return oferta_prof


if __name__ == '__main__':
    # arquivo_de_emails(in_file='relatorios/Acompanhamento/Alunos/ALUTEL/2017-2.txt')

    # csv_com_entrada_saida_de_alunos('relatorios/Planejamento/Curso/CUREGEP/' + f for f in ['1997.txt', '1998.txt', '2000.txt', '2002.txt', '2004.txt', '2006.txt', '2008.txt', '2010.txt', '2012.txt', '2014.txt', '2016.txt'])

    turmas = turmas_ofertadas(['guilherme'], 'relatorios/Planejamento/Oferta/OFELST/2017-2.txt')

    pass
