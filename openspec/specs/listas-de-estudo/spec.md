# listas-de-estudo Specification

## Purpose
TBD - created by archiving change libras-anki-deck. Update Purpose after archive.
## Requirements
### Requirement: Listas de estudo em arquivos de texto

O sistema MUST aceitar como entrada arquivos de texto contendo palavras ou frases, um item por linha, e DEVE tratar cada arquivo como um agrupamento temático mantido pelo usuário.

A interpretação de cada linha MUST depender apenas do prefixo `=` (força tratamento como palavra) e da resolução contra o dicionário. O sistema MUST NOT usar nenhum separador de glosa para decidir o tipo da linha.

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

### Requirement: Pendências viram tags, nunca omissão

O sistema MUST NOT descartar em silêncio nenhum item das listas. Todo item sem material completo MUST gerar nota marcada para preenchimento manual.

#### Scenario: Palavra sem verbete

- **WHEN** uma palavra da lista não é resolvida contra o dicionário
- **THEN** uma nota é criada com a tag `falta-video` em vez de o item ser omitido

#### Scenario: Filtragem no Anki

- **WHEN** o usuário busca por `tag:falta-video` no Anki
- **THEN** obtém a lista do que precisa completar com material das aulas

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

#### Scenario: Frase da lista

- **WHEN** uma frase da lista é processada
- **THEN** a nota é criada com um único card, cujo verso lista os vídeos das palavras reconhecidas

#### Scenario: Palavra da frase ausente do dicionário

- **WHEN** uma frase contém uma palavra que não existe no INES
- **THEN** o verso do card indica explicitamente qual palavra não tem sinal disponível

#### Scenario: Nenhuma tag de glosa

- **WHEN** qualquer nota de frase é criada
- **THEN** ela não recebe a tag `falta-glosa`, que deixou de existir

