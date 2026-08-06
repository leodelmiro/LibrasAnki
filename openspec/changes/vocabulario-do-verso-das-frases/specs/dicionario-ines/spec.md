## MODIFIED Requirements

### Requirement: Busca tolerante a acento, caixa e flexão

O sistema MUST resolver termos escritos em português corrente contra a base do INES, que é em caixa alta, acentuada, no infinitivo e com sufixo numérico para desambiguar homônimos. A resolução MUST tentar, em ordem: exato, normalizado, sem sufixo numérico, plural simples, lematizado e por sinônimo.

A remoção do sufixo numérico MUST tolerar espaço antes do número. A base usa os dois formatos — `ABANDONAR2` colado e `DIA 1` com espaço — e tratar apenas o primeiro deixa palavras inalcançáveis e parte em dois grupos verbetes que pertencem ao mesmo sinal.

O sistema MUST poder excluir verbetes do índice quando a normalização os tornar indistinguíveis de outro de sentido sem relação. O termo pedido MUST continuar resolvendo normalmente; apenas o verbete excluído MUST NOT aparecer no resultado. Isso é distinto do bloqueio de falso amigo, que recusa o termo inteiro e devolve o motivo.

Ao extrair as palavras significativas de uma frase, o sistema MUST reconhecer sequências de palavras declaradas como um sinal único, e MUST fazê-lo antes de descartar as palavras funcionais. Depois do descarte a informação necessária não existe mais: em "por que", `que` é funcional e sairia, e `por` sozinho é falso amigo do verbo colocar.

A sequência reconhecida MUST substituir as palavras que a compõem por um único item de vocabulário, e o casamento MUST ser tentado da sequência mais longa para a mais curta, para que uma expressão que comece igual a outra não seja partida pela mais curta.

O que a tabela declara MUST ser um termo a resolver, e não um verbete escolhido. Assim uma expressão que corresponda a uma palavra de vários sentidos continua devolvendo todos eles, em vez de a tabela fixar um sentido de passagem.

#### Scenario: Correspondência direta

- **WHEN** a lista contém `casa`
- **THEN** o verbete `CASA` é resolvido

#### Scenario: Diferença de acento e caixa

- **WHEN** a lista contém `voce`
- **THEN** o verbete `VOCÊ` é resolvido

#### Scenario: Verbo flexionado

- **WHEN** a lista contém `cheguei`
- **THEN** a lematização resolve para `CHEGAR` e os verbetes correspondentes são retornados

#### Scenario: Termo com sinônimo mapeado

- **WHEN** a lista contém `mãe`, que não existe como verbete
- **THEN** a tabela de sinônimos resolve para `MAMÃE` e os verbetes correspondentes são retornados

#### Scenario: Termo sem correspondência

- **WHEN** a lista contém um termo que não existe em nenhuma forma, como `média`
- **THEN** o sistema reporta o termo como não resolvido em vez de omiti-lo silenciosamente

#### Scenario: Sufixo numérico separado por espaço

- **WHEN** a lista contém `dia`, cujos verbetes no INES são `DIA 1` a `DIA 4`
- **THEN** os quatro verbetes são resolvidos, do mesmo modo que aconteceria com o sufixo colado

#### Scenario: Verbete com os dois formatos de sufixo

- **WHEN** um sinal tem verbetes escritos nos dois formatos, como `MAIS 1` junto de `MAIS2` a `MAIS6`
- **THEN** todos caem no mesmo grupo, em vez de serem classificados como sinais distintos

#### Scenario: Falso amigo bloqueado

- **WHEN** o usuário escreve um termo que a normalização levaria a um verbete de sentido completamente diferente
- **THEN** a resolução falha com o motivo registrado, em vez de devolver o verbete errado

#### Scenario: Verbete excluído por colisão de normalização

- **WHEN** dois verbetes de sentidos sem relação viram a mesma chave depois da normalização e um deles está na lista de excluídos
- **THEN** o termo resolve apenas para o verbete mantido, e uma única nota é gerada

#### Scenario: Expressão cujos pedaços são funcionais

- **WHEN** a frase contém `O que`, cujas duas palavras seriam descartadas como funcionais
- **THEN** a sequência é reconhecida antes do descarte e vira um item de vocabulário, em vez de a expressão sumir da frase

#### Scenario: Expressão cujo pedaço é falso amigo

- **WHEN** a frase contém `Por que`
- **THEN** a sequência resolve para o sinal da pergunta, sem que `por` sozinho chegue ao bloqueio de falso amigo

#### Scenario: Expressão cujos pedaços resolvem para sinais errados

- **WHEN** a frase contém `mais ou menos`, cujas três palavras resolvem individualmente para sinais de comparação, alternativa e subtração
- **THEN** a sequência é reconhecida como um item só, e os três sinais avulsos não entram no vocabulário

#### Scenario: Expressão que corresponde a palavra de vários sentidos

- **WHEN** a sequência reconhecida resolve para uma palavra que tem mais de um verbete no INES
- **THEN** todos os verbetes são devolvidos, porque a tabela declara um termo e não um verbete
