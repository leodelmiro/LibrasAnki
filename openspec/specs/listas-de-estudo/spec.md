# listas-de-estudo Specification

## Purpose
TBD - created by archiving change libras-anki-deck. Update Purpose after archive.
## Requirements
### Requirement: Listas de estudo em arquivos de texto

O sistema MUST aceitar como entrada arquivos de texto contendo palavras ou frases, um item por linha, e DEVE tratar cada arquivo como um agrupamento temático mantido pelo usuário.

A interpretação de cada linha MUST depender apenas do prefixo `=` (força tratamento como palavra) e da resolução contra o dicionário. O sistema MUST NOT usar nenhum separador de glosa para decidir o tipo da linha.

Uma linha MUST poder declarar um vídeo de fora do INES para o seu item, com o marcador `@yt`. Essa declaração MUST ser separada do texto antes de a linha ser interpretada, de modo que a URL não participe da decisão entre palavra e frase.

#### Scenario: Lista de palavras

- **WHEN** um arquivo contém uma palavra por linha
- **THEN** cada linha é resolvida contra o dicionário e produz uma nota

#### Scenario: Lista de frases

- **WHEN** uma linha contém uma frase completa em português
- **THEN** ela é tratada como frase e não como palavra isolada

#### Scenario: Comentários e linhas vazias

- **WHEN** uma linha está vazia ou começa com `#`
- **THEN** ela é ignorada

#### Scenario: Agrupamento não vem do campo assunto

- **WHEN** o usuário quer um baralho de saudações ou possessivos
- **THEN** o agrupamento vem do arquivo de lista, e não de consulta ao campo `assunto` do INES, que não possui essas categorias

#### Scenario: Linha com barra vertical

- **WHEN** uma linha contém o caractere `|`
- **THEN** ele é tratado como texto comum, sem significado especial, e a linha é interpretada pelas mesmas regras das demais

#### Scenario: Palavra única com vídeo declarado

- **WHEN** uma linha traz uma palavra seguida de `@yt` e uma URL
- **THEN** o item continua sendo a palavra, e a URL não faz a linha ser interpretada como frase

### Requirement: Pendências viram tags, nunca omissão

O sistema MUST NOT descartar em silêncio nenhum item das listas. Todo item sem material completo MUST gerar nota marcada para preenchimento manual.

Quando a linha declarar um vídeo de fora do INES e o clipe for obtido, ele MUST ter precedência sobre qualquer outra fonte de vídeo daquele item, e a nota MUST receber a tag `video-externo` sem receber `falta-video`.

O sistema MUST distinguir a forma que não existe em LIBRAS do item que não tem material. Uma forma que é transporte do português — cuja tradução correta é outro sinal que o dicionário tem — MUST gerar card mostrando o vídeo do sinal correto, MUST receber a tag `forma-incorreta`, e MUST NOT receber `falta-video`. O card MUST continuar existindo com a palavra incorreta na frente: é ele que desfaz o engano de quem vem do português.

Itens compostos — que não têm verbete próprio porque se sinalizam em sequência — MUST ser montados a partir dos vídeos dos componentes quando estes existirem no dicionário, e MUST receber a tag `composto`. Nesse caso o sistema MUST NOT aplicar `falta-video`, porque não há nada a gravar para o card funcionar.

Os componentes de um composto MUST refletir como a expressão se sinaliza, e não a tradução palavra por palavra do português. Um composto montado por tradução literal produz um card que parece completo e ensina uma sequência inexistente, o que é pior que um card vazio.

Quando a escolha de um componente resultar de eliminação entre homônimos, e não de conhecimento confirmado, a nota MUST receber a tag `confirmar-sinal` e o card MUST dizer o que precisa ser checado.

#### Scenario: Palavra sem verbete

- **WHEN** uma palavra da lista não é resolvida contra o dicionário, não é um composto conhecido, não é forma incorreta conhecida e não declara vídeo externo
- **THEN** uma nota é criada com a tag `falta-video` em vez de o item ser omitido

#### Scenario: Filtragem no Anki

- **WHEN** o usuário busca por `tag:falta-video` no Anki
- **THEN** obtém a lista do que precisa completar com material das aulas

#### Scenario: Forma que não existe em LIBRAS

- **WHEN** um item da lista é transporte do português cuja forma correta é outro sinal do dicionário
- **THEN** o card mostra o vídeo do sinal correto, a observação diz qual é e por quê, e a nota recebe `forma-incorreta` sem receber `falta-video`

#### Scenario: Composto que não é tradução literal

- **WHEN** a expressão se sinaliza de forma diferente da sequência das palavras em português
- **THEN** os componentes declarados são os do sinal real, e não os das palavras traduzidas uma a uma

#### Scenario: Lacuna preenchida por vídeo externo

- **WHEN** uma palavra sem verbete no INES declara um vídeo externo e o clipe é obtido
- **THEN** o card mostra o clipe, recebe `video-externo` e não recebe `falta-video`

#### Scenario: Vídeo externo tem precedência sobre componentes

- **WHEN** um item é um composto conhecido e também declara vídeo externo
- **THEN** o card mostra o clipe declarado, e os componentes não são montados

#### Scenario: Composto com componentes disponíveis

- **WHEN** um item da lista é um composto conhecido e seus componentes têm vídeo no INES
- **THEN** o card mostra os vídeos dos componentes em sequência, cada um rotulado com o nome do sinal, e a nota recebe `composto` sem receber `falta-video`

#### Scenario: Composto com escolha de homônimo

- **WHEN** um componente foi escolhido por eliminação entre homônimos de sentidos diferentes
- **THEN** a nota recebe `confirmar-sinal` e a observação do card nomeia o que confirmar na aula

#### Scenario: Componente sem vídeo

- **WHEN** um componente declarado não é encontrado ou não tem vídeo
- **THEN** o card informa qual componente ficou de fora, em vez de omiti-lo silenciosamente

#### Scenario: Composto sem nenhum componente disponível

- **WHEN** nenhum componente de um composto pôde ser resolvido
- **THEN** a nota recebe `falta-video`, como qualquer item sem material

### Requirement: Cards de contraste para números de 1 a 10

O sistema MUST tratar os números de 1 a 10 como contraste entre funções gramaticais, e não como vocabulário isolado, quando o dicionário oferecer mais de um verbete para o mesmo número.

#### Scenario: Número com dois verbetes

- **WHEN** o número tem dois verbetes com descrições distintas, como `UM1` e `UM2`
- **THEN** é gerado um card que apresenta os dois vídeos e pergunta qual corresponde a cada função, explicando a diferença no verso

#### Scenario: Número com verbete único

- **WHEN** o número tem apenas um verbete, como `QUATRO`
- **THEN** são gerados os cards de recepção e produção normais

#### Scenario: Forma ordinal ausente

- **WHEN** a forma ordinal com movimento trêmulo é requisitada
- **THEN** a nota é criada com a tag `falta-video`, pois essa distinção não existe no dataset do INES

#### Scenario: Escopo limitado a 1 a 10

- **WHEN** a lista de números é processada
- **THEN** apenas 1 a 10 é contemplado, faixa em que o dicionário tem cobertura completa

### Requirement: Cards de frase sem notação escrita

O sistema MUST gerar um card por frase, exibindo o vocabulário reconhecido no verso. O sistema MUST NOT armazenar nem exibir glosa em LIBRAS, e MUST NOT marcar frases com tag de glosa pendente.

Quando o dicionário oferecer mais de um sinal para uma palavra da frase, o sistema MUST exibir todos, e MUST NOT escolher um por posição no dicionário. Escolher por posição produz card completo que ensina o sinal errado, que é pior que um card que declara a dúvida: em "Quem mora com você?", o primeiro verbete de `QUEM` é o de identificar o proprietário de um objeto.

Cada opção MUST vir rotulada com a descrição que o dicionário dá daquele verbete. É a descrição que permite escolher; sem ela o card apenas empurraria a dúvida adiante.

A contagem MUST ser de sinais, e não de verbetes. Verbetes que o dicionário agrupa como variantes do mesmo sinal MUST continuar produzindo um vídeo só, porque ali não há escolha nenhuma a oferecer.

A nota MUST receber tag própria quando oferecer escolha, e a observação MUST nomear as palavras afetadas, de modo que essas frases possam ser encontradas no Anki e revisadas.

Uma sequência de palavras reconhecida como sinal único MUST ocupar uma posição só no vocabulário do verso, rotulada pelo termo que o dicionário conhece.

#### Scenario: Frase da lista

- **WHEN** uma frase da lista é processada
- **THEN** a nota é criada com um único card, cujo verso lista os vídeos das palavras reconhecidas

#### Scenario: Palavra da frase ausente do dicionário

- **WHEN** uma frase contém uma palavra que não existe no INES
- **THEN** o verso do card indica explicitamente qual palavra não tem sinal disponível

#### Scenario: Nenhuma tag de glosa

- **WHEN** qualquer nota de frase é criada
- **THEN** ela não recebe a tag `falta-glosa`, que deixou de existir

#### Scenario: Palavra com mais de um sinal no dicionário

- **WHEN** uma palavra da frase resolve para vários sinais de sentidos distintos
- **THEN** o verso mostra todos, cada um sob a descrição do dicionário, e a nota recebe a tag de escolha com as palavras afetadas na observação

#### Scenario: Variantes do mesmo sinal não viram escolha

- **WHEN** uma palavra da frase resolve para verbetes que o dicionário agrupa como variantes do mesmo sinal
- **THEN** o verso mostra um vídeo só, sem rótulo de sentido e sem a tag de escolha

#### Scenario: Expressão de várias palavras no vocabulário

- **WHEN** uma sequência reconhecida como sinal único aparece na frase
- **THEN** ela ocupa uma posição só no verso, e as palavras que a compõem não aparecem separadas

#### Scenario: Palavra com sinal único

- **WHEN** uma palavra da frase resolve para um sinal só
- **THEN** o verso mostra o vídeo rotulado apenas com a palavra, sem a descrição do dicionário

