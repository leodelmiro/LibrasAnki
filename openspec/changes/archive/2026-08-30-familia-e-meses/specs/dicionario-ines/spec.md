## MODIFIED Requirements

### Requirement: Busca tolerante a acento, caixa e flexão

O sistema MUST resolver termos escritos em português corrente contra a base do INES, que é em caixa alta, acentuada, no infinitivo e com sufixo numérico para desambiguar homônimos. A resolução MUST tentar, em ordem: exato, normalizado, sem sufixo numérico, plural simples, lematizado e por sinônimo.

Quando a forma pedida estiver no plural simples e a busca pelo singular falhar, o sistema MUST reaplicar as tabelas de lema e de sinônimo sobre o singular antes de desistir. Sem isso o plural falha justamente onde o singular resolveria — `avós` para, `avó` passa — e cada entrada das tabelas teria de ser repetida nas duas formas, que é duplicação que envelhece mal.

A remoção do sufixo numérico MUST tolerar espaço antes do número. A base usa os dois formatos — `ABANDONAR2` colado e `DIA 1` com espaço — e tratar apenas o primeiro deixa palavras inalcançáveis e parte em dois grupos verbetes que pertencem ao mesmo sinal.

O sistema MUST poder excluir verbetes do índice quando a normalização os tornar indistinguíveis de outro de sentido sem relação. O termo pedido MUST continuar resolvendo normalmente; apenas o verbete excluído MUST NOT aparecer no resultado. Isso é distinto do bloqueio de falso amigo, que recusa o termo inteiro e devolve o motivo.

Ao extrair as palavras significativas de uma frase, o sistema MUST reconhecer sequências de palavras declaradas como um sinal único, e MUST fazê-lo antes de descartar as palavras funcionais. Depois do descarte a informação necessária não existe mais: em "por que", `que` é funcional e sairia, e `por` sozinho é falso amigo do verbo colocar.

A sequência reconhecida MUST substituir as palavras que a compõem por um único item de vocabulário, e o casamento MUST ser tentado da sequência mais longa para a mais curta, para que uma expressão que comece igual a outra não seja partida pela mais curta.

O que a tabela declara MUST ser um termo a resolver, e não um verbete escolhido. Assim uma expressão que corresponda a uma palavra de vários sentidos continua devolvendo todos eles, em vez de a tabela fixar um sentido de passagem.

Um verbete cujo nome contenha caractere que a normalização não remove — a barra de `AVÔ/AVÓ1`, por exemplo — MUST ser alcançável por sinônimo declarado, já que nenhuma escrita corrente do termo chega até ele.

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

#### Scenario: Plural de termo que só resolve por sinônimo

- **WHEN** uma frase contém `cunhadas`, cujo singular `cunhada` não tem verbete e resolve por sinônimo para `CUNHADO`
- **THEN** o plural é reduzido ao singular e a tabela de sinônimos é aplicada sobre ele, resolvendo para `CUNHADO`

#### Scenario: Plural de termo que só resolve por lema

- **WHEN** uma frase contém uma forma plural cujo singular só é alcançável pela tabela de lemas
- **THEN** a lematização é aplicada sobre o singular, em vez de a resolução falhar

#### Scenario: Verbete inalcançável pela escrita corrente

- **WHEN** o nome do verbete contém barra, como `AVÔ/AVÓ1`, e nenhuma escrita de `avô` ou `avó` normaliza para ele
- **THEN** o termo só resolve se houver sinônimo declarado, e sem esse sinônimo o sistema o reporta como não resolvido em vez de devolver verbete de outro sinal

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

### Requirement: Download de vídeos sob demanda

O sistema MUST baixar de `https://dicionario.ines.gov.br/public/media/palavras/videos/<video>` apenas os arquivos das palavras efetivamente solicitadas, mantendo-os em cache local.

Quando a nota já tiver vídeo obtido de fora do INES, o sistema MUST NOT requisitar o vídeo do INES para ela: o arquivo não seria usado, e a rede é o recurso caro do processo.

O sistema MUST admitir que a base declare o nome de um arquivo de vídeo que o servidor não entrega. Nesse caso MUST tentar, em ordem, duas recuperações antes de desistir.

A primeira é pelo **nome do arquivo**: o sistema MUST tentar o mesmo nome com o sufixo numérico trocado, porque a base erra esse sufixo com frequência e o arquivo certo está no servidor sob outro número. Um candidato só MUST ser aceito se **nenhum outro verbete o declarar como seu**. Sem essa guarda a recuperação pega o vídeo do vizinho: `SER2` declara `ser3Sm`, que dá 404, e o primeiro nome que responde é `ser1Sm` — o vídeo de `SER1`, outro sinal. Aceito o candidato, a nota MUST receber a tag `video-renomeado` e registrar na observação o arquivo que foi usado.

A segunda é pelo **sinal**: quando outro verbete do dicionário mostrar o mesmo sinal, a nota MUST usar o vídeo desse outro verbete, receber a tag `mesmo-sinal` e registrar na observação de onde o vídeo veio.

As duas MUST ser tentadas apenas depois de o download próprio falhar, para que a nota volte sozinha ao vídeo dela se o servidor for corrigido.

O sistema MUST NOT emprestar vídeo entre verbetes de sinais apenas parecidos: mostrar um sinal por outro ensina o errado com aparência de certo.

#### Scenario: Vídeo ainda não baixado

- **WHEN** uma nota referencia um vídeo ausente do cache
- **THEN** o arquivo é baixado e gravado no cache

#### Scenario: Vídeo já em cache

- **WHEN** uma nota referencia um vídeo já presente no cache
- **THEN** nenhuma requisição de rede é feita

#### Scenario: Download falha

- **WHEN** a requisição de um vídeo não retorna sucesso, nenhuma variante de nome responde, nenhum outro verbete mostra o mesmo sinal e nenhuma fonte externa foi declarada
- **THEN** a nota é gerada com a tag `falta-video` e a falha é registrada no relatório

#### Scenario: Sufixo do arquivo errado na base

- **WHEN** o verbete `JUNHO` declara `junho1Sm_Prog001.mp4`, que responde 404, e `junhoSm_Prog001.mp4` responde 200 sem ser declarado por nenhum outro verbete
- **THEN** a nota usa `junhoSm_Prog001.mp4`, recebe `video-renomeado` e não recebe `falta-video`

#### Scenario: Variante de nome pertence a outro verbete

- **WHEN** o verbete `SER2` declara `ser3Sm_Prog001.mp4`, que responde 404, e a variante `ser1Sm_Prog001.mp4` responde 200 mas é o vídeo declarado por `SER1`
- **THEN** essa variante é recusada, e a recuperação segue para as demais ou falha, em vez de servir o vídeo de outro sinal

#### Scenario: Vídeo declarado que o servidor não entrega

- **WHEN** o verbete tem nome de arquivo preenchido, o servidor responde 404, nenhuma variante de nome livre responde e outro verbete mostra o mesmo sinal
- **THEN** a nota usa o vídeo do outro verbete, recebe `mesmo-sinal` e não recebe `falta-video`

#### Scenario: Campo de imagem é ignorado

- **WHEN** um verbete possui o campo `image` preenchido
- **THEN** o sistema não tenta baixá-lo, pois o diretório `public/media/palavras/images/` retorna 404

#### Scenario: Nota servida por vídeo externo

- **WHEN** a linha da lista declara um vídeo de fora e o clipe é obtido
- **THEN** o vídeo do INES daquele verbete não é requisitado
