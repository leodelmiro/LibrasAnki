## Context

O baralho tratava toda ausência de vídeo do mesmo jeito: tag `falta-video` e o aviso "grave na aula". Investigar os 20 cards nessa situação mostrou que a maioria não era o que a mensagem dizia.

```
o que o card dizia          o que era de fato
──────────────────          ──────────────────
FEMININO                    verbete existe, vídeo declarado,
  ⚠ Sem vídeo — grave       servidor responde 404 — e o
    na aula                 mesmo sinal está em MULHER

TEU                         não existe em LIBRAS; o sinal
  ⚠ Sem verbete no INES,    de 2ª pessoa é SEU, que o
    preencher com aula      baralho já tem

FIM DE SEMANA               montado como FIM + SEMANA,
  FIM   [vídeo]             tradução literal do português;
  SEMANA[vídeo]             sinaliza-se SÁBADO + DOMINGO

CARNE (2 cards)             CARNÊ entrou por colisão de
  o alimento / o bloco      normalização, e é de outro
  de pagamento              universo
```

Quatro problemas distintos com a mesma cara.

## Goals / Non-Goals

**Goals:**

- Separar os quatro casos, para que o card diga a verdade sobre por que está como está.
- Aproveitar o que o próprio INES já tem quando ele tem, mesmo que sob outra entrada.
- Manter cada decisão declarada e revisável, como `COMPOSTOS` já é.

**Non-Goals:**

- Varrer a base atrás de todos os 404. São 5.824 verbetes e a varredura custaria uma requisição por vídeo; os casos entram quando aparecem nas listas.
- Detectar automaticamente que dois verbetes são o mesmo sinal. Exigiria entender relação semântica — o projeto já recusou isso em `marcar_videos_compartilhados`, que marca e deixa a decisão para quem estuda.
- Corrigir a base do INES ou reportar os 404 a eles. Fora do alcance.

## Decisions

### 1. Quatro tabelas, não uma

A tentação é uma tabela só de "casos especiais". Elas fazem coisas diferentes e caem em pontos diferentes do fluxo:

| tabela | pergunta que responde | onde atua |
|---|---|---|
| `IGNORADOS` | este verbete deveria estar no índice? | `Indice.__init__`, antes de qualquer busca |
| `MESMO_SINAL` | o vídeo faltou, mas outro verbete mostra o mesmo sinal? | `_nota_de_sinal`, depois de o download falhar |
| `CORRECOES` | esta forma existe na língua? | `_nota_ausente`, ao lado de `COMPOSTOS` |
| `NOTAS_DE_SINAL` | o verbete explica a si mesmo? | `_nota_de_sinal`, sempre |

Juntá-las obrigaria a um campo de tipo e a um `if` por caso na hora de aplicar — mais código para dizer a mesma coisa, e uma tabela que só se entende lendo o código que a consome.

### 2. `IGNORADOS` é diferente de `FALSOS_AMIGOS`

O índice já tinha um mecanismo parecido: `FALSOS_AMIGOS` bloqueia `LIBRAS` e `POR`, porque a normalização os levaria a `LIBRA` (peso) e `PÔR` (colocar). Mas ele bloqueia **o termo inteiro** — resolver "libras" devolve nada, com o motivo.

`carne` é outro caso: o termo deve resolver, e resolver certo. O que sobra é um verbete parasita no resultado. Por isso `IGNORADOS` age antes, tirando o verbete do índice, em vez de recusar a busca.

```
FALSOS_AMIGOS          IGNORADOS
─────────────          ─────────
"libras" → nada        "carne" → [CARNE]
  + motivo                       (CARNÊ nunca entrou no índice)
```

### 3. Empréstimo de vídeo só quando é o mesmo sinal

`MESMO_SINAL` poderia virar "sinônimo com vídeo", aceitando pares aproximados. Não vai: o card ensina um sinal, e mostrar o vídeo de um sinal parecido ensina o errado com cara de certo.

`FEMININO` → `MULHER` entra porque é o mesmo sinal, não porque as palavras se aproximam. A observação do card diz "Mesmo sinal de MULHER", então quem estuda sabe o que está vendo, e a tag `mesmo-sinal` permite auditar a lista inteira depois.

O degrau só é tentado **depois** de o download do vídeo próprio falhar. Se o INES consertar o 404 amanhã, o card volta sozinho para o vídeo dele, sem mudança de código.

### 4. Forma incorreta continua sendo card

O caminho mais curto para `teu` seria tirá-lo das listas — se não existe, não estuda. Mas o erro é justamente o que precisa ser desfeito: quem vem do português vai tentar dizer "teu", e o card existe para interceptar isso.

Por isso `teu` mantém a palavra na frente, mostra o vídeo de `SEU` no verso, e a observação diz por quê. É o mesmo raciocínio de `surdo mudo`, que já estava no baralho como termo a reconhecer e recusar.

Vale para `tua` pelo mesmo motivo, com a nota de que `SEU` não marca gênero.

### 5. `fim de semana` é composto, não lacuna

O comentário de `dias-da-semana.txt` dizia que `FIM DE SEMANA` "não existe como verbete no INES" e que existe no VLibras — tratando como lacuna do dicionário. Não é: a expressão se sinaliza nomeando os dois dias, do mesmo jeito que `BOA TARDE` se sinaliza `BOA` + `TARDE`.

O erro anterior não era só de classificação. `FIM` + `SEMANA` são dois verbetes que existem, então o card mostrava dois vídeos e parecia certo — traduzia o português palavra por palavra e ensinava uma sequência que ninguém usa. Um card errado com aparência de completo é pior que um card vazio.

## Risks / Trade-offs

- **As quatro tabelas crescem à mão.** É o mesmo custo de `COMPOSTOS`, aceito pelo mesmo motivo: automatizar erraria em silêncio nos casos que importam.
- **`IGNORADOS` esconde um verbete de verdade.** Se algum dia `CARNÊ` fizer falta, escrever `CARNÊ` na lista não o traz de volta — ele saiu do índice. O comentário na tabela registra isso.
- **O empréstimo depende do 404 continuar.** Se o INES arrumar o vídeo de `FEMININO`, o empréstimo para de acontecer e a entrada em `MESMO_SINAL` vira código morto silencioso. O bloco `VÍDEO EMPRESTADO` no relatório expõe isso: quando o nome sumir da lista, a entrada pode sair.
