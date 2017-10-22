#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


from sigra import acompanhamento
from sigra import planejamento


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
    relacao = acompanhamento.Alunos.ALUTEL(in_file, encoding=encoding)
    emails = [contact.format(nome=info['nome'], email=info['e-mail'],
                             telefone=info['telefone'])
              for info in relacao.values()]

    with open(out_file, 'w') as f:
        f.write('\n'.join(email for email in sorted(emails)))


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
    oferta = planejamento.Oferta.OFELIST(in_file, encoding)
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
    # arquivo_de_emails(in_file='ALUTEL.txt')

    # turmas = turmas_ofertadas(['guilherme'], 'OFELIST.txt'))

    pass
