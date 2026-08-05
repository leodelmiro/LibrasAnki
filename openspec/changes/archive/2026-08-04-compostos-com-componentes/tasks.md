> Implementação feita antes destes artefatos, durante a conversa que originou a
> mudança. As tarefas abaixo descrevem o que foi executado e verificado; ficam
> marcadas por refletirem o estado real do código, não por terem sido planejadas
> primeiro.

## 1. Investigação

- [x] 1.1 Testar se os componentes dos 6 compostos resolvem no INES, um a um
- [x] 1.2 Levantar os homônimos envolvidos e ler a descrição de cada um (`BOM` tem 3, `BOA` tem 2)
- [x] 1.3 Diagnosticar por que `dia` não resolve e medir o alcance do defeito (9 verbetes com espaço, 4 palavras-base afetadas)

## 2. Correção do índice

- [x] 2.1 Trocar `_SUFIXO_NUMERICO` de `\d+$` para `\s*\d+$` em `indice.py`, com comentário explicando os dois formatos do INES
- [x] 2.2 Atualizar o docstring de `raiz()` com o segundo exemplo (`DIA 1 -> DIA`)
- [x] 2.3 Verificar quais raízes mudam e confirmar que nenhuma está nas listas atuais

## 3. Tabela de compostos

- [x] 3.1 Trocar `COMPOSTOS` de `str -> str` para `str -> Composto(nota, sinais, confirmar)`
- [x] 3.2 Declarar os componentes dos 6 compostos por nome exato de verbete
- [x] 3.3 Escrever, em comentário, o motivo de cada escolha de homônimo e por que os componentes não são derivados por split
- [x] 3.4 Marcar em `confirmar` os componentes escolhidos por eliminação

## 4. Montagem da nota

- [x] 4.1 Acrescentar `componentes` a `modelo.criar_nota`, usando `html_vocabulario` quando presente
- [x] 4.2 Documentar no docstring por que componentes não passam por `pares_video`
- [x] 4.3 Criar `Gerador._componentes`, resolvendo por nome exato e devolvendo também os que faltaram
- [x] 4.4 Reescrever `_nota_ausente` para montar os componentes, aplicar `composto` e `confirmar-sinal`, e só aplicar `falta-video` quando não houver componente nenhum
- [x] 4.5 Acrescentar ao card a lista de componentes que ficaram de fora, quando houver

## 5. Relatório

- [x] 5.1 Acrescentar `Relatorio.compostos` e o bloco "COMPOSTOS" com a sequência de cada um
- [x] 5.2 Ajustar a dica do bloco "SEM SINAL NO INES", que afirmava que todos ficam com `falta-video`

## 6. Documentação

- [x] 6.1 Acrescentar `composto` e `confirmar-sinal` à tabela de tags do README
- [x] 6.2 Acrescentar a seção "Compostos" ao README, com o exemplo e o motivo de os componentes serem declarados à mão
- [x] 6.3 Corrigir o comentário de `listas/saudacoes.txt`, que dizia que esses itens ficam com `falta-video`

## 7. Verificação

- [x] 7.1 Gerar o baralho e conferir que os 6 compostos aparecem no bloco COMPOSTOS com a sequência esperada
- [x] 7.2 Inspecionar o `.apkg` e confirmar, por composto, os vídeos rotulados, as tags e a observação
- [x] 7.3 Confirmar que a contagem por tipo não mudou (123 notas, mesma distribuição)
- [x] 7.4 Confirmar que `falta-video` caiu de 25 para 19 notas e que `composto`=6 e `confirmar-sinal`=4
- [x] 7.5 Confirmar que itens não compostos (`ótimo`, `terça-feira`) seguem com `falta-video` e o aviso
- [x] 7.6 Reimportar no Anki e conferir que os 6 compostos ganharam os vídeos sem perder histórico — **passo manual no app**
