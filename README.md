SIGRA
=====

Implementação de funções que manipulam dados de relatórios do Sistema de Graduação da UnB ([SIGRA](http://cpd.unb.br/ssi-sis-academicos)).

O diretório [`sigra`](https://github.com/UnB-CIC/SIGRAExtractor/tree/master/sigra) define um módulo com o código para lidar com os relatórios emitidos pelo SIGRA, que devem ser exportados como arquivos `.txt`, com a codificação [UTF-16](https://pt.wikipedia.org/wiki/UTF-16). Cada relatório tem sua própria função de uso, seguindo a hierarquia de menus do SIGRA.

O diretório [`coordenacao`](https://github.com/UnB-CIC/SIGRAExtractor/tree/master/coordenacao) define um módulo para lidar com os dados extraídos dos relatórios, consolidando-os como informações úteis.

Exemplo de Uso
--------------
Verificar a média de alunos de determinado curso, matriculados  em uma disciplina, por semestre.

```Python
from coordenacao import alunos

relacao_de_alunos = 'relatorios/acompanhamento/alunos/ALUREL.txt'
# Supõe-se que seja caminho para o arquivo (UTF-16) contendo a
# relação de alunos a serem considerados.

lista_matriculados = 'relatorios/acompanhamento/historico/HEDIS.txt'
# Supõe-se que seja caminho para o arquivo (UTF-16) contendo o
# histórico de desempenho em uma disciplina.

lista = alunos.matriculados_por_semestre(relacao_de_alunos,
                                         lista_matriculados)

ignora_verao = True
filtro_de_semestre = '2014/2 <= {} <= 2017/2'
print(alunos.media_de_matriculados_por_semestre(lista, ignora_verao,
                                                filtro_de_semestre))
```
