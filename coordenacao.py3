#  -*- coding: utf-8 -*-
#    @package: coordenacao.py3
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções úteis para coordenação.


from sigra import acompanhamento


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


if __name__ == '__main__':
    # arquivo_de_emails(in_file='ALUTEL.txt')
    pass
