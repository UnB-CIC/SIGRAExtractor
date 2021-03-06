#  -*- coding: utf-8 -*-
#    @package: disciplina.py
#     @author: Guilherme N. Ramos (gnramos@unb.br)
#
# Funções de extração de informações de relatórios de Planejamento do Sistema
# de Graduação da UnB (SIGRA).

import re
from sigra import utils


def listagem(arquivo):
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
        nome = m.group(3).strip().title()
        rest = m.group(4).strip()
        creditos = utils.Creditos.to_string(m.group(5).strip(),
                                            m.group(6).strip(),
                                            m.group(7).strip(),
                                            m.group(8).strip())
        domi = m.group(9)
        return orgao, nivel, nome, rest, creditos, domi

    lines = preprocess(utils.load(arquivo))

    relacao = {}
    i = 1
    num_lines = len(lines)
    while i < num_lines:
        if eh_disciplina(lines[i]):
            # No caso de disciplinas "repetidas", considera apenas a última
            # informação. Ex: 181315 que é listada em ADM e EPR.
            (orgao, nivel, nome, rest,
             creditos, domi) = parse_disciplina(lines[i])
            i += 1
            codigo, resto_do_nome = re.search(r'(\d{6})(.*)',
                                              lines[i]).groups()
            if resto_do_nome:
                nome += ' ' + resto_do_nome.strip().title()

            i += 1

            pre_reqs = ''
            while i < num_lines and not eh_disciplina(lines[i]):
                m = re.search(r'^ {100,}(\d{6})$', lines[i])
                if m:
                    pre_reqs += m.group(1)
                else:
                    m = re.search(r'^ {100,}(E|OU)$', lines[i])
                    if m:
                        pre_reqs += m.group(1)
                i += 1
            i -= 1  # Saiu da repetição, mas será incrementado novamente

            pre_reqs = utils.parse_pre_requisitos(pre_reqs)
            relacao[codigo] = {'Nome': nome,
                               'Órgão': orgao,
                               'Créditos': creditos,
                               'Pré-requisitos': pre_reqs}

        i += 1

    print('{} disciplinas listadas.'.format(len(relacao)))
    return relacao
