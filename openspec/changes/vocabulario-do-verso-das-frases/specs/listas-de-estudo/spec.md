## MODIFIED Requirements

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
