> Implementação feita antes destes artefatos, durante a conversa que originou a
> mudança. As tarefas abaixo descrevem o que foi executado e verificado; ficam
> marcadas por refletirem o estado real do código, não por terem sido planejadas
> primeiro.

## 1. Investigação

- [x] 1.1 Levantar os 20 cards com `falta-video` e separar por causa real
- [x] 1.2 Confirmar que `FEMININO`, `DORMIR`, `PESSOA1` e `VOVÓ-VOVÔ` têm verbete e nome de vídeo, e que o servidor responde 404
- [x] 1.3 Confirmar que `MULHER` tem verbete e que o vídeo dela baixa normalmente
- [x] 1.4 Confirmar que `CARNE` e `CARNÊ` viram a mesma chave depois da normalização

## 2. Verbetes ignorados

- [x] 2.1 Criar `IGNORADOS` em `indice.py`, filtrando `self.verbetes` na construção do `Indice`
- [x] 2.2 Comparar por raiz da palavra, para pegar também eventuais sufixos numéricos
- [x] 2.3 Documentar em comentário a diferença para `FALSOS_AMIGOS`, que bloqueia o termo inteiro
- [x] 2.4 Confirmar que `carne` passa a gerar um card só e que `CARNE MOÍDA` não foi afetada

## 3. Vídeo emprestado

- [x] 3.1 Criar `MESMO_SINAL` e `TAG_MESMO_SINAL` em `gerador.py`
- [x] 3.2 Aplicar em `_nota_de_sinal` apenas depois de o download próprio falhar, reaproveitando `_componentes` para resolver o alvo
- [x] 3.3 Acrescentar a observação com a origem do vídeo
- [x] 3.4 Documentar em comentário que só entra quando é o mesmo sinal, não sinônimo aproximado

## 4. Formas incorretas

- [x] 4.1 Criar o namedtuple `Correcao` e a tabela `CORRECOES`
- [x] 4.2 Tratar correção ao lado de composto em `_nota_ausente`, com a tag `forma-incorreta`
- [x] 4.3 Declarar `teu` e `tua` apontando para `SEU`, com a nota de que `SEU` não marca gênero
- [x] 4.4 Retirar `teu` e `tua` de `NOTAS_DE_LINGUA`, deixando um comentário dizendo para onde foram

## 5. Observações por sinal

- [x] 5.1 Criar `NOTAS_DE_SINAL`, aplicada em `_nota_de_sinal`
- [x] 5.2 Declarar `VOVÓ-VOVÔ` como um sinal só para os dois avós, marcado com o feminino

## 6. Compostos corrigidos

- [x] 6.1 Acrescentar `fim de semana` como `SÁBADO` + `DOMINGO`, com o motivo em comentário
- [x] 6.2 Corrigir `tenha um bom fim de semana` de `BOM` + `FIM` + `SEMANA` para `BOM` + `SÁBADO` + `DOMINGO`

## 7. Relatório

- [x] 7.1 Acrescentar `Relatorio.correcoes` e o bloco "FORMA INCORRETA"
- [x] 7.2 Acrescentar `Relatorio.mesmo_sinal` e o bloco "VÍDEO EMPRESTADO"
- [x] 7.3 Separar as correções do bloco "COMPOSTOS", que passaria a misturar dois conceitos

## 8. Conteúdo

- [x] 8.1 Acrescentar `forma-incorreta` e `mesmo-sinal` à tabela de tags do README
- [x] 8.2 Corrigir o comentário de `dias-da-semana.txt`, que tratava `fim de semana` como lacuna do INES
- [x] 8.3 Corrigir o comentário de `pronomes-possessivos.txt`, que descrevia configuração de mão para `TEU`/`TUA`
- [x] 8.4 Corrigir o comentário de `vocabulario-diverso.txt` sobre `carne`/`CARNÊ` e registrar os casos de 404
- [x] 8.5 Corrigir o comentário de `familia.txt` sobre `VOVÓ-VOVÔ`

## 9. Verificação

- [x] 9.1 Gerar o baralho e confirmar `CARNE` e `CARNE MOÍDA` presentes, `CARNÊ` ausente
- [x] 9.2 Confirmar o bloco "FORMA INCORRETA" com `teu = SEU` e `tua = SEU`
- [x] 9.3 Confirmar o bloco "VÍDEO EMPRESTADO" com `FEMININO = MULHER`
- [x] 9.4 Confirmar `fim de semana = SÁBADO + DOMINGO` e `tenha um bom fim de semana = BOM + SÁBADO + DOMINGO` no bloco COMPOSTOS
- [x] 9.5 Reimportar no Anki e conferir que `teu`, `tua` e `feminino` ganharam vídeo sem perder histórico, e que a nota de `CARNÊ` foi removida à mão do navegador — **passo manual no app**
