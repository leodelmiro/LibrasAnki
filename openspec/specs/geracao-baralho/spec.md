# geracao-baralho Specification

## Purpose
TBD - created by archiving change libras-anki-deck. Update Purpose after archive.
## Requirements
### Requirement: GUID estável para reimportação incremental

O sistema MUST derivar o GUID de cada nota de `ident` combinado com o nome do arquivo de vídeo, de modo que regerar e reimportar o baralho atualize as notas existentes sem duplicá-las nem apagar o histórico de revisão.

A origem do vídeo efetivamente exibido MUST NOT participar do cálculo do GUID. Acrescentar, trocar ou remover um vídeo de fora do INES MUST atualizar a nota existente, e MUST NOT criar outra: um card que ganha vídeo continua sendo o mesmo card, com o histórico de revisão que já tinha.

#### Scenario: Reimportação após acrescentar palavras

- **WHEN** o baralho é regerado com palavras novas e reimportado no Anki
- **THEN** as notas anteriores são atualizadas mantendo o histórico e apenas as novas são acrescentadas

#### Scenario: Campo posicional não é usado

- **WHEN** o GUID é calculado
- **THEN** o campo `id` não participa do cálculo, por ser posicional e mudar quando o INES insere verbetes

#### Scenario: Correção de template após importação

- **WHEN** um template é corrigido e o baralho é regerado e reimportado
- **THEN** os cards existentes refletem a correção sem perda de agendamento

#### Scenario: Card que ganha vídeo externo

- **WHEN** uma palavra que estava com `falta-video` recebe um vídeo externo e o baralho é reimportado
- **THEN** a nota existente é atualizada com o vídeo, preservando o agendamento, em vez de uma nota nova ser criada

### Requirement: Reprodução de vídeo em desktop e AnkiMobile

O sistema MUST embutir os vídeos usando um elemento `<video>` com os atributos `autoplay`, `loop`, `muted` e `playsinline`, contendo dois elementos `<source>`: WebM primeiro, MP4 em seguida. O webview do Anki desktop não decodifica H.264 e o WebKit do iOS não decodifica WebM em versões mais antigas, então cada plataforma seleciona o formato que sabe reproduzir.

Esse requisito MUST valer para qualquer vídeo do baralho, independentemente da origem: as duas plataformas continuam sendo as mesmas e as limitações de codec também.

O sistema MUST NOT embutir vídeo por referência remota — `<iframe>` ou `<source>` apontando para uma URL. O baralho MUST continuar autocontido e reproduzível offline, e o player embutido do YouTube não funciona no AnkiMobile.

Quando não houver vídeo disponível, o sistema MUST escrever um aviso no lugar do elemento `<video>`, dentro do mesmo campo, de modo que o card continue sendo gerado.

#### Scenario: Revisão no Anki desktop

- **WHEN** um card com vídeo é revisado no Anki desktop
- **THEN** o vídeo WebM é reproduzido dentro do card

#### Scenario: Revisão no AnkiMobile

- **WHEN** um card com vídeo é revisado no AnkiMobile
- **THEN** o vídeo é reproduzido dentro do card, sem abrir em tela cheia

#### Scenario: Sinal curto

- **WHEN** um card com vídeo é exibido
- **THEN** o vídeo repete em laço, permitindo observar um sinal de cerca de um segundo mais de uma vez

#### Scenario: Sinal sem vídeo disponível

- **WHEN** um sinal não tem vídeo no INES, o download falhou e nenhuma outra fonte foi declarada
- **THEN** o campo de vídeo contém um aviso legível no lugar do elemento `<video>`, e tanto o card de recepção quanto o de produção continuam sendo gerados

#### Scenario: Clipe de fora do INES

- **WHEN** um card exibe um vídeo obtido de fora do INES
- **THEN** ele é embutido pelo mesmo elemento `<video>` com os dois formatos, a partir de arquivos empacotados no `.apkg`

### Requirement: Conversão dos vídeos para WebM

O sistema MUST produzir WebM/VP9 e MP4/H.264 para cada vídeo do baralho, qualquer que seja a origem, e incluir os dois formatos no pacote, mantendo os resultados em cache para não repetir o trabalho.

Vídeos do INES já chegam em MP4/H.264 e MUST ser apenas convertidos para WebM. Vídeos de fora MUST ser convertidos para os dois formatos, porque a fonte não tem formato garantido.

A conversão MUST fixar o pixel format em 4:2:0. VP9 em 4:4:4 é profile 1, e nem todo webview decodifica profile diferente de 0.

#### Scenario: Vídeo ainda não convertido

- **WHEN** um vídeo MP4 é usado por uma nota e não existe WebM correspondente em cache
- **THEN** a conversão é executada e o resultado é gravado em cache

#### Scenario: Conversão já em cache

- **WHEN** o WebM correspondente já existe em cache
- **THEN** a conversão não é executada novamente

#### Scenario: Conversão falha

- **WHEN** a conversão de um vídeo do INES falha
- **THEN** a nota é gerada apenas com o MP4 e a falha é registrada no relatório

#### Scenario: Variante com múltiplos vídeos

- **WHEN** uma nota classificada como variante contém mais de um vídeo
- **THEN** todos são exibidos no mesmo card, identificados individualmente

#### Scenario: Fonte externa em formato arbitrário

- **WHEN** um vídeo de fora é obtido em qualquer codec ou resolução
- **THEN** os dois formatos do baralho são produzidos a partir dele, com a largura limitada

### Requirement: Pacote Anki autocontido

O sistema MUST produzir um arquivo `.apkg` com toda a mídia embutida, importável em Anki desktop e AnkiMobile sem arquivos externos.

#### Scenario: Geração do pacote

- **WHEN** a geração termina
- **THEN** um único arquivo `.apkg` contendo notas, templates e vídeos é escrito no destino indicado

#### Scenario: Importação sem dependências externas

- **WHEN** o `.apkg` é importado em uma instalação limpa do Anki
- **THEN** todos os vídeos são reproduzidos sem exigir pasta de mídia adicional

### Requirement: Relatório de execução

O sistema MUST emitir, ao final da geração, um resumo das notas criadas e de tudo que exigiu atenção. O relatório MUST NOT conter seção de glosa pendente. O relatório MUST listar como cada composto foi montado, para que a escolha dos componentes seja revisável sem abrir o Anki.

O relatório MUST listar as formas incorretas com o sinal que as substituiu, e os vídeos emprestados com o verbete de origem. As tabelas que decidem esses dois casos são mantidas à mão, e o relatório é onde elas ficam auditáveis: quando um verbete deixar de aparecer no bloco de vídeo emprestado, a entrada correspondente pode sair da tabela.

O relatório MUST registrar os problemas de escrita das próprias listas, com origem e número da linha, e MUST registrar as falhas de obtenção de vídeo externo com o motivo. Nenhum dos dois MUST interromper a geração.

O relatório MUST listar as frases cujo verso oferece escolha de sentido, nomeando as palavras e quantas opções cada uma tem. Essa é a lista do que perguntar na aula: cada linha é uma escolha que o dicionário não soube fazer e que o baralho está deixando em aberto de propósito.

#### Scenario: Resumo ao final

- **WHEN** a geração termina
- **THEN** o relatório informa quantas notas foram criadas, quantas receberam cada tag de pendência, e lista os termos não resolvidos

#### Scenario: Anomalias listadas

- **WHEN** notas recebem a tag `video-suspeito` ou `grupo-misto`
- **THEN** o relatório lista as palavras afetadas para conferência manual

#### Scenario: Sem bloco de glosa

- **WHEN** o relatório é emitido
- **THEN** nenhum bloco "SEM GLOSA" é impresso, porque a glosa deixou de fazer parte do baralho

#### Scenario: Compostos listados

- **WHEN** compostos foram montados a partir dos componentes
- **THEN** o relatório lista cada um com a sequência usada, no formato `boa tarde = BOA + TARDE`

#### Scenario: Formas incorretas listadas

- **WHEN** notas de forma incorreta foram geradas
- **THEN** o relatório lista cada uma com o sinal correto, no formato `teu = SEU`

#### Scenario: Vídeos emprestados listados

- **WHEN** uma nota usou o vídeo de outro verbete por o seu não ter sido obtido
- **THEN** o relatório lista o par, no formato `FEMININO = MULHER`, com a explicação de que o vídeo próprio não foi entregue

#### Scenario: Linha de lista malformada

- **WHEN** uma linha declara um vídeo externo de forma que não pode ser interpretada
- **THEN** o relatório a lista com o arquivo, o número da linha e o motivo, e o card daquela linha é gerado assim mesmo

#### Scenario: Vídeo externo não obtido

- **WHEN** o download ou o recorte de um vídeo externo falha
- **THEN** o relatório lista o link e o motivo, e informa que o card ficou com o vídeo do INES ou sem vídeo

#### Scenario: Um link para vários sinais

- **WHEN** um item que declara vídeo externo resolve para mais de um sinal no INES
- **THEN** o relatório informa que o vídeo foi aplicado ao primeiro e nomeia qual foi

#### Scenario: Frases com escolha de sentido listadas

- **WHEN** o verso de uma frase oferece mais de um sinal para alguma palavra
- **THEN** o relatório lista a frase com as palavras afetadas e a quantidade de opções de cada uma

### Requirement: Modelo de nota por tipo de item

O sistema MUST gerar uma nota por sinal, com os templates de card determinados pelo tipo do item. Palavras MUST ter dois templates — recepção e produção. Frases MUST ter um único template — sinalizar. O sistema MUST NOT gerar card de gramática em nenhum dos modelos: o baralho pratica sinais, não notação escrita.

A nota de palavra MUST conter apenas os campos `Palavra`, `Videos`, `Descricao`, `Origem` e `Observacao`. O sistema MUST NOT incluir exemplo, glosa, configuração de mão nem classe gramatical na nota de palavra.

O campo de vídeo da nota de palavra MUST aceitar duas formas de conteúdo: o vídeo do sinal próprio, ou os vídeos de componentes rotulados quando o item for composto. Componentes MUST ser rotulados individualmente com o nome do sinal e apresentados na ordem de sinalização; o sistema MUST NOT rotulá-los como variantes, porque não são formas alternativas do mesmo sinal.

#### Scenario: Card de recepção

- **WHEN** o card de recepção é exibido
- **THEN** a frente mostra o vídeo do sinal e o verso mostra a palavra em português, a descrição e, quando houver, a observação

#### Scenario: Card de produção

- **WHEN** o card de produção é exibido
- **THEN** a frente mostra a palavra em português e o verso mostra o vídeo, a origem quando houver, e a observação quando houver

#### Scenario: Palavra não gera card de gramática

- **WHEN** uma nota de palavra é criada
- **THEN** exatamente dois cards são gerados, e nenhum card de gramática existe

#### Scenario: Card de frase

- **WHEN** o card de frase é exibido
- **THEN** a frente mostra a frase em português e o verso mostra os vídeos do vocabulário reconhecido, cada um sob a palavra correspondente

#### Scenario: Frase não gera card de gramática

- **WHEN** uma nota de frase é criada
- **THEN** exatamente um card é gerado

#### Scenario: Nota de item composto

- **WHEN** a nota de um composto é exibida
- **THEN** o campo de vídeo traz os vídeos dos componentes em sequência, cada um sob o nome do seu sinal, e não sob rótulo de variante

