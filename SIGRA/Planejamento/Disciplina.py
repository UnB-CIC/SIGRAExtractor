#  -*- coding: utf-8 -*-
#    @package: Disciplina.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Planejamento do Sistema
# de Graduação da UnB (SIGRA).

import re

from SIGRA import utils


def Listagem(arquivo):
    '''Retorna um dicionário com as informações de cada disciplina
    ofertada, extraindo as informações do arquivo de entrada.

    Argumentos:
    arquivo -- caminho para o arquivo (UTF-16) contendo os dados, que deve ser
               o relatório exportado via:
               SIGRA > Planejamento > Disciplina > DISLST

    No caso de pré-requisitos, veja a função utils.parse_pre_requisitos.
    '''
    def preprocess(content):
        HEADER = r'Universidade de Brasília.*[\s\S]*?Relação de Disciplinas.*?'
        FOOTER = r'  --+[\s\S].*lstdislst'

        content = re.sub(HEADER, '', content)
        content = re.sub(FOOTER, '', content)

        return [line for line in content.split('\n') if line.strip()]

    def eh_disciplina(line):
        REGEX = r'^ +([A-Z]{1,5}) +([A-Z]{2,})  +(.*?)  +(.*?)  +' \
                '(\d{3}) +(\d{3}) +(\d{3}) +(\d{3}) +(.*)$'
        return re.search(REGEX, line)

    def eh_pre_req(line):
        return re.search(r'^  +([A-z]{3})$', line)

    def parse_disciplina(line):
        m = eh_disciplina(line)
        orgao = m.group(1).strip()
        nivel = m.group(2).strip()
        nome = utils.capitalize(m.group(3).strip())
        rest = m.group(4).strip()
        creditos = utils.Creditos.to_string(m.group(5).strip(),
                                            m.group(6).strip(),
                                            m.group(7).strip(),
                                            m.group(8).strip())
        domi = m.group(9)
        return orgao, nivel, nome, rest, creditos, domi

    content = preprocess(utils.load(arquivo))

    print('Extração de dados.')
    relacao = {}
    i = 1
    num_lines = len(content)
    while i < num_lines:
        if eh_disciplina(content[i]):
            # No caso de disciplinas "repetidas", considera apenas a última
            # informação. Ex: 181315 que é listada em ADM e EPR.
            (orgao, nivel, nome, rest,
             creditos, domi) = parse_disciplina(content[i])
            i += 1
            codigo, resto_do_nome = re.search(r'(\d{6})(.*)',
                                              content[i]).groups()
            if resto_do_nome:
                nome += ' ' + utils.capitalize(resto_do_nome.strip())

            i += 1

            pre_reqs = ''
            while i < num_lines and not eh_disciplina(content[i]):
                m = re.search(r'^ {100,}(\d{6})$', content[i])
                if m:
                    pre_reqs += m.group(1)
                else:
                    m = re.search(r'^ {100,}(E|OU)$', content[i])
                    if m:
                        pre_reqs += m.group(1)
                i += 1
            i -= 1  # Saiu da repetição, mas será incrementado novamente

            pre_reqs = utils.parse_pre_requisitos(pre_reqs)
            relacao[codigo] = {'Nome': nome, 'Órgão': orgao,
                               'Créditos': creditos,
                               'Pré-requisitos': pre_reqs}

        i += 1

    print('{} disciplinas.'.format(len(relacao)))
    return relacao
