## MODIFIED Requirements

### Requirement: Busca tolerante a acento, caixa e flexão

O sistema MUST resolver termos escritos em português corrente contra a base do INES, que é em caixa alta, acentuada, no infinitivo e com sufixo numérico para desambiguar homônimos. A resolução MUST tentar, em ordem: exato, normalizado, sem sufixo numérico, plural simples, lematizado e por sinônimo.

A remoção do sufixo numérico MUST tolerar espaço antes do número. A base usa os dois formatos — `ABANDONAR2` colado e `DIA 1` com espaço — e tratar apenas o primeiro deixa palavras inalcançáveis e parte em dois grupos verbetes que pertencem ao mesmo sinal.

O sistema MUST poder excluir verbetes do índice quando a normalização os tornar indistinguíveis de outro de sentido sem relação. O termo pedido MUST continuar resolvendo normalmente; apenas o verbete excluído MUST NOT aparecer no resultado. Isso é distinto do bloqueio de falso amigo, que recusa o termo inteiro e devolve o motivo.

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

### Requirement: Download de vídeos sob demanda

O sistema MUST baixar de `https://dicionario.ines.gov.br/public/media/palavras/videos/<video>` apenas os arquivos das palavras efetivamente solicitadas, mantendo-os em cache local.

O sistema MUST admitir que a base declare o nome de um arquivo de vídeo que o servidor não entrega. Quando o download falhar e outro verbete do dicionário mostrar o mesmo sinal, a nota MUST usar o vídeo desse outro verbete, receber a tag `mesmo-sinal` e registrar na observação de onde o vídeo veio. Essa alternativa MUST ser tentada apenas depois de o download próprio falhar, para que a nota volte sozinha ao vídeo dela se o servidor for corrigido.

O sistema MUST NOT emprestar vídeo entre verbetes de sinais apenas parecidos: mostrar um sinal por outro ensina o errado com aparência de certo.

#### Scenario: Vídeo ainda não baixado

- **WHEN** uma nota referencia um vídeo ausente do cache
- **THEN** o arquivo é baixado e gravado no cache

#### Scenario: Vídeo já em cache

- **WHEN** uma nota referencia um vídeo já presente no cache
- **THEN** nenhuma requisição de rede é feita

#### Scenario: Download falha

- **WHEN** a requisição de um vídeo não retorna sucesso e nenhum outro verbete mostra o mesmo sinal
- **THEN** a nota é gerada com a tag `falta-video` e a falha é registrada no relatório

#### Scenario: Vídeo declarado que o servidor não entrega

- **WHEN** o verbete tem nome de arquivo preenchido, o servidor responde 404 e outro verbete mostra o mesmo sinal
- **THEN** a nota usa o vídeo do outro verbete, recebe `mesmo-sinal` e não recebe `falta-video`

#### Scenario: Campo de imagem é ignorado

- **WHEN** um verbete possui o campo `image` preenchido
- **THEN** o sistema não tenta baixá-lo, pois o diretório `public/media/palavras/images/` retorna 404
