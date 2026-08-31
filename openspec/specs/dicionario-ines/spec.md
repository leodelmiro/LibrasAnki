# dicionario-ines Specification

## Purpose
TBD - created by archiving change libras-anki-deck. Update Purpose after archive.
## Requirements
### Requirement: Obtenção e cache do dataset

O sistema MUST obter o dataset do INES a partir de `https://dicionario.ines.gov.br/public/site/js/palavras.js`, extrair o array JSON e mantê-lo em cache local, reutilizando o cache em execuções seguintes sem acessar a rede.

#### Scenario: Primeira execução sem cache

- **WHEN** o sistema é executado e não existe cache local
- **THEN** o `palavras.js` é baixado, o trecho entre o primeiro `[` e o último `]` é interpretado como JSON, e o resultado é gravado em cache

#### Scenario: Execução seguinte com cache válido

- **WHEN** o sistema é executado e existe cache local válido
- **THEN** o dataset é lido do cache e nenhuma requisição ao `palavras.js` é feita

#### Scenario: Estrutura do arquivo mudou

- **WHEN** o conteúdo baixado não contém um array JSON interpretável com os campos esperados
- **THEN** o sistema falha com mensagem indicando que o formato do INES mudou, e o cache anterior é preservado

#### Scenario: Verbetes inativos são descartados

- **WHEN** o dataset é carregado
- **THEN** verbetes com `status` igual a `0` são excluídos do índice

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

### Requirement: Classificação de grupos com sufixo numérico

O sistema MUST agrupar verbetes que compartilham a mesma raiz seguida de sufixo numérico e classificar cada grupo como variante ou homônimo comparando `descricao` e `classe`.

#### Scenario: Descrição e classe idênticas

- **WHEN** o grupo `ALMOÇO1`/`ALMOÇO2` tem a mesma `descricao` e a mesma `classe`
- **THEN** o grupo é classificado como variante e produz uma única nota contendo os dois vídeos

#### Scenario: Descrições distintas

- **WHEN** o grupo `OBRIGADO1`/`OBRIGADO2` tem descrições diferentes
- **THEN** o grupo é classificado como homônimo e produz uma nota por verbete, cada uma exibindo sua própria descrição

#### Scenario: Grupo misto

- **WHEN** um grupo tem parte dos verbetes com descrição igual e parte diferente
- **THEN** cada verbete produz uma nota separada e todas recebem a tag `grupo-misto`

### Requirement: Marcação de anomalias da base

O sistema MUST detectar inconsistências conhecidas do dataset e marcar as notas afetadas em vez de falhar ou propagar dado incorreto.

#### Scenario: Vídeo compartilhado por verbetes distintos

- **WHEN** um mesmo arquivo de vídeo é referenciado por mais de um verbete
- **THEN** todas as notas envolvidas recebem a tag `video-suspeito` e o caso é listado no relatório de execução

#### Scenario: Linha corrompida de DOIS2

- **WHEN** o verbete `DOIS2` aparece em duas linhas com o mesmo `ident` e uma delas referencia `doar2Sm_Prog001.mp4`
- **THEN** a linha cujo nome de vídeo não corresponde ao prefixo da palavra é descartada

#### Scenario: Identificador duplicado

- **WHEN** dois verbetes ativos compartilham o mesmo `ident`
- **THEN** o nome do arquivo de vídeo é usado como desempate para mantê-los distintos

### Requirement: Download de vídeos sob demanda

O sistema MUST baixar de `https://dicionario.ines.gov.br/public/media/palavras/videos/<video>` apenas os arquivos das palavras efetivamente solicitadas, mantendo-os em cache local.

Quando a nota já tiver vídeo obtido de fora do INES, o sistema MUST NOT requisitar o vídeo do INES para ela: o arquivo não seria usado, e a rede é o recurso caro do processo.

O sistema MUST admitir que a base declare o nome de um arquivo de vídeo que o servidor não entrega. Quando o download falhar e outro verbete do dicionário mostrar o mesmo sinal, a nota MUST usar o vídeo desse outro verbete, receber a tag `mesmo-sinal` e registrar na observação de onde o vídeo veio. Essa alternativa MUST ser tentada apenas depois de o download próprio falhar, para que a nota volte sozinha ao vídeo dela se o servidor for corrigido.

O sistema MUST NOT emprestar vídeo entre verbetes de sinais apenas parecidos: mostrar um sinal por outro ensina o errado com aparência de certo.

#### Scenario: Vídeo ainda não baixado

- **WHEN** uma nota referencia um vídeo ausente do cache
- **THEN** o arquivo é baixado e gravado no cache

#### Scenario: Vídeo já em cache

- **WHEN** uma nota referencia um vídeo já presente no cache
- **THEN** nenhuma requisição de rede é feita

#### Scenario: Download falha

- **WHEN** a requisição de um vídeo não retorna sucesso, nenhum outro verbete mostra o mesmo sinal e nenhuma fonte externa foi declarada
- **THEN** a nota é gerada com a tag `falta-video` e a falha é registrada no relatório

#### Scenario: Vídeo declarado que o servidor não entrega

- **WHEN** o verbete tem nome de arquivo preenchido, o servidor responde 404 e outro verbete mostra o mesmo sinal
- **THEN** a nota usa o vídeo do outro verbete, recebe `mesmo-sinal` e não recebe `falta-video`

#### Scenario: Campo de imagem é ignorado

- **WHEN** um verbete possui o campo `image` preenchido
- **THEN** o sistema não tenta baixá-lo, pois o diretório `public/media/palavras/images/` retorna 404

#### Scenario: Nota servida por vídeo externo

- **WHEN** a linha da lista declara um vídeo de fora e o clipe é obtido
- **THEN** o vídeo do INES daquele verbete não é requisitado

