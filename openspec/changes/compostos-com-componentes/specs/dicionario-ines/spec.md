## MODIFIED Requirements

### Requirement: Busca tolerante a acento, caixa e flexão

O sistema MUST resolver termos escritos em português corrente contra os verbetes do INES, aplicando em ordem: correspondência exata, normalização de acento e caixa, remoção de sufixo numérico, e uma tabela de lematização de flexões comuns.

A remoção do sufixo numérico MUST tolerar espaço entre a palavra e o número. O INES usa os dois formatos — `ABANDONAR2` na maioria dos casos e `DIA 1` em nove verbetes — e tratar apenas o primeiro deixa palavras inalcançáveis e parte em dois grupos verbetes que pertencem ao mesmo sinal.

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

- **WHEN** a lista contém `atrasado`, que não existe em nenhuma forma
- **THEN** o sistema reporta o termo como não resolvido em vez de omiti-lo silenciosamente

#### Scenario: Sufixo numérico separado por espaço

- **WHEN** a lista contém `dia`, cujos verbetes no INES são `DIA 1` a `DIA 4`
- **THEN** os quatro verbetes são resolvidos, do mesmo modo que aconteceria com o sufixo colado

#### Scenario: Verbete com os dois formatos de sufixo

- **WHEN** um sinal tem verbetes escritos nos dois formatos, como `MAIS 1` junto de `MAIS2` a `MAIS6`
- **THEN** todos caem no mesmo grupo, em vez de serem classificados como sinais distintos
