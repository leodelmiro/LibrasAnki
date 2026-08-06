## MODIFIED Requirements

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
