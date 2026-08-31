## Context

O verso da frase é o card de produção do baralho: o português na frente, e atrás os vídeos do vocabulário para conferir sinal por sinal. Ele era montado assim:

```
palavras_da_frase(texto)  ->  para cada palavra: resolver -> verbetes[0] -> vídeo
```

Duas perdas nesse caminho, e nenhuma delas aparecia no campo de aviso do card — o que as tornava piores que uma lacuna declarada. Auditando as 38 frases palavra por palavra:

```
antes                                          depois
─────                                          ──────
O que você gosta de fazer?                     O que você gosta de fazer?
  você  gosta  fazer                             que — impossibilidade de compreensão
  ("O que" some, sem aviso)                      que — indaga a escolha de alguém
                                                 você  gosta  fazer

Quem mora com você?                            Quem mora com você?
  Quem  -> QUEM1, "proprietário de um            Quem — proprietário de um objeto
           objeto" (a frase é sobre gente)       Quem — autor de uma informação
  mora  você                                     Quem — identificar ou nominar alguém
                                                 mora  você
```

## Goals / Non-Goals

**Goals:**

- Não perder sinal na quebra da frase em palavras.
- Não ensinar um sinal escolhido às cegas com aparência de escolha informada.
- Manter a auditoria possível sem abrir o Anki: o relatório diz onde há escolha.

**Non-Goals:**

- Declarar qual sentido cada frase usa. Exige conhecimento de LIBRAS que o dicionário não fornece.
- Desambiguar por contexto automaticamente. As descrições do INES são frase corrida em português; casar isso com a frase da lista seria adivinhação com aparência de método, que é o erro que esta change corrige.
- Mexer nos cards de palavra. Homônimos já viram um card cada, e ali a separação é o produto, não um problema.

## Decisions

### 1. O casamento de expressão vem antes do descarte das funcionais

`palavras_da_frase` descartava palavras funcionais (`VAZIAS`) e devolvia o resto. Reconhecer "por que" depois disso é impossível: o "que" já foi embora.

A alternativa era tratar a expressão na resolução, depois da quebra — juntar palavras vizinhas ao consultar o dicionário. Descartada: a quebra é o ponto em que a informação de adjacência ainda existe, e reconstruí-la depois significaria carregar a posição de cada palavra por todo o caminho para usar em dois casos.

O casamento é do maior para o menor. Hoje nenhuma expressão é prefixo de outra, mas "mais ou menos" tem três palavras e "por que" tem duas: sem a ordem, uma expressão futura que comece igual a outra mais curta seria partida pela curta.

### 2. O valor da tabela é um termo, não um verbete

`EXPRESSOES` mapeia para o texto que o resolvedor vai consultar, não para o verbete final:

```python
("O", "QUE"): "que"        # resolve, e devolve QUE1 e QUE2
("POR", "QUE"): "porque"   # resolve para PORQUE
```

Apontar direto para `QUE2` seria possível — a resolução tem passo exato, e casaria. Mas fixaria a escolha do sentido dentro de uma tabela que existe para outra coisa, e escondê-la ali é o oposto do que a decisão 3 faz. Mapeando para o termo, "o que" cai naturalmente nos dois verbetes e o card mostra os dois.

O rótulo exibido no verso é o termo da tabela, não a frase original: o card do "O que você gosta de fazer?" mostra `que`, e não `O que`. É a palavra que o dicionário conhece.

### 3. Mostrar todos os sentidos, em vez de escolher um

Três saídas eram possíveis quando o INES tem mais de um sinal para a palavra da frase:

| | pegar o primeiro | tabela `(frase, palavra) → verbete` | mostrar todos |
|---|---|---|---|
| card fica completo | sim | sim | sim |
| pode ensinar errado | **sim, em silêncio** | não | não |
| exige saber LIBRAS | não | **sim, para cada frase** | não |
| custo por frase nova | zero | uma entrada à mão | zero |

A tabela é a resposta certa quando o conhecimento existe — é como os `COMPOSTOS` funcionam. Mas ela não pode ser preenchida com o que o dicionário oferece: a descrição do INES é suficiente para provar que `QUAL1` ("identificar um local") está errado na frase do prato, e insuficiente para dizer se o certo é `QUAL2` ou `QUAL3`. Preencher assim mesmo seria trocar um chute silencioso por um chute declarado.

Mostrar todos põe a escolha em quem está sinalizando, junto com a informação para decidir. A tabela continua possível depois, sem desmanchar nada: ela passaria a filtrar o que hoje é mostrado inteiro.

### 4. O rótulo é a descrição do INES, não o nome do verbete

`qual 1`, `qual 2`, `qual 3` não dizem nada a quem está com o card na mão. `qual — Expressão com que se busca identificar um local` diz. A descrição é o que torna a escolha possível, então é ela que vai no rótulo; sem ela o card só empurraria a dúvida adiante.

### 5. Contar sinais, não verbetes

`MEU1` e `MEU2` têm a mesma descrição — são o mesmo sinal em dois verbetes, e o agrupamento já os trata como variante. Oferecer os dois como "escolha" seria inventar uma decisão onde não há nenhuma, e treinar a ignorar o rótulo nas frases em que a escolha é real.

`_sinais_de` percorre os verbetes da resolução e devolve os `Sinal` distintos, pela identidade do objeto. Cinco grupos que pareciam escolha somem por aí: `MEU`, `FOLGA`, e os demais pares de descrição idêntica.

## Risks / Trade-offs

- **Verso longo onde o INES é bagunçado.** `IR` tem 6 sentidos, então "Como você vai trabalhar?" mostra 6 vídeos só para o "vai", em 5 frases. Dois deles (`IR1` e `IR3`) têm descrição idêntica e ainda assim são sinais separados na base — é o grupo já marcado como `grupo-misto`. Aceito por ora: o card fica pesado, mas honesto. Mitigação disponível quando o sentido for confirmado em aula: a tabela da decisão 3.
- **O rótulo carrega a descrição inteira do INES**, que em alguns verbetes é longa. Truncar economizaria espaço e tiraria justamente a informação que justifica o rótulo existir.
- **`EXPRESSOES` é mantida à mão**, como `LEMAS` e `SINONIMOS`. Cresce por descoberta, uma frase de cada vez. É a mesma escolha já feita no resto do módulo: uma tabela manual erra menos, e erra visivelmente, comparada a heurística que erra em silêncio.
- **A frase do kg mudou de texto**, e o GUID da nota de frase deriva do texto. A nota antiga fica órfã no Anki de quem já importou, e o Anki não apaga nota que deixou de ser gerada. Sem mitigação automática: é apagar à mão no navegador, como já documentado no README para o caso dos templates removidos.
