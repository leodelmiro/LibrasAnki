## ADDED Requirements

### Requirement: Modelo de nota único com três templates

O sistema MUST gerar uma nota por sinal, com três templates de card — recepção, produção e gramática — em vez de notas separadas por direção.

#### Scenario: Sinal com exemplo e glosa completos

- **WHEN** uma nota tem `exemplo` e `libras` preenchidos
- **THEN** três cards são gerados: recepção, produção e gramática

#### Scenario: Sinal sem exemplo ou sem glosa

- **WHEN** uma nota não tem `exemplo` ou não tem `libras`
- **THEN** apenas os cards de recepção e produção são gerados, sem card de gramática vazio

#### Scenario: Card de recepção

- **WHEN** o card de recepção é exibido
- **THEN** a frente mostra o vídeo do sinal e o verso mostra a palavra em português, a descrição e o exemplo

#### Scenario: Card de produção

- **WHEN** o card de produção é exibido
- **THEN** a frente mostra a palavra em português com a classe gramatical e o verso mostra o vídeo, a configuração de mão e a glosa

#### Scenario: Card de gramática

- **WHEN** o card de gramática é exibido
- **THEN** a frente mostra a frase em português e o verso mostra a frase em português junto da glosa em LIBRAS

### Requirement: GUID estável para reimportação incremental

O sistema MUST derivar o GUID de cada nota de `ident` combinado com o nome do arquivo de vídeo, de modo que regerar e reimportar o baralho atualize as notas existentes sem duplicá-las nem apagar o histórico de revisão.

#### Scenario: Reimportação após acrescentar palavras

- **WHEN** o baralho é regerado com palavras novas e reimportado no Anki
- **THEN** as notas anteriores são atualizadas mantendo o histórico e apenas as novas são acrescentadas

#### Scenario: Campo posicional não é usado

- **WHEN** o GUID é calculado
- **THEN** o campo `id` não participa do cálculo, por ser posicional e mudar quando o INES insere verbetes

#### Scenario: Correção de template após importação

- **WHEN** um template é corrigido e o baralho é regerado e reimportado
- **THEN** os cards existentes refletem a correção sem perda de agendamento

### Requirement: Reprodução de vídeo em desktop e AnkiMobile

O sistema MUST embutir os vídeos usando um elemento `<video>` com os atributos `autoplay`, `loop`, `muted` e `playsinline`, contendo dois elementos `<source>`: WebM primeiro, MP4 em seguida. O webview do Anki desktop não decodifica H.264 e o WebKit do iOS não decodifica WebM em versões mais antigas, então cada plataforma seleciona o formato que sabe reproduzir.

#### Scenario: Revisão no Anki desktop

- **WHEN** um card com vídeo é revisado no Anki desktop
- **THEN** o vídeo WebM é reproduzido dentro do card

#### Scenario: Revisão no AnkiMobile

- **WHEN** um card com vídeo é revisado no AnkiMobile
- **THEN** o vídeo é reproduzido dentro do card, sem abrir em tela cheia

#### Scenario: Sinal curto

- **WHEN** um card com vídeo é exibido
- **THEN** o vídeo repete em laço, permitindo observar um sinal de cerca de um segundo mais de uma vez

### Requirement: Conversão dos vídeos para WebM

O sistema MUST converter cada vídeo do INES para WebM/VP9 e incluir os dois formatos no pacote, mantendo as conversões em cache para não repetir o trabalho.

#### Scenario: Vídeo ainda não convertido

- **WHEN** um vídeo MP4 é usado por uma nota e não existe WebM correspondente em cache
- **THEN** a conversão é executada e o resultado é gravado em cache

#### Scenario: Conversão já em cache

- **WHEN** o WebM correspondente já existe em cache
- **THEN** a conversão não é executada novamente

#### Scenario: Conversão falha

- **WHEN** a conversão de um vídeo falha
- **THEN** a nota é gerada apenas com o MP4 e a falha é registrada no relatório

#### Scenario: Variante com múltiplos vídeos

- **WHEN** uma nota classificada como variante contém mais de um vídeo
- **THEN** todos são exibidos no mesmo card, identificados individualmente

### Requirement: Pacote Anki autocontido

O sistema MUST produzir um arquivo `.apkg` com toda a mídia embutida, importável em Anki desktop e AnkiMobile sem arquivos externos.

#### Scenario: Geração do pacote

- **WHEN** a geração termina
- **THEN** um único arquivo `.apkg` contendo notas, templates e vídeos é escrito no destino indicado

#### Scenario: Importação sem dependências externas

- **WHEN** o `.apkg` é importado em uma instalação limpa do Anki
- **THEN** todos os vídeos são reproduzidos sem exigir pasta de mídia adicional

### Requirement: Relatório de execução

O sistema MUST emitir, ao final da geração, um resumo das notas criadas e de tudo que exigiu atenção.

#### Scenario: Resumo ao final

- **WHEN** a geração termina
- **THEN** o relatório informa quantas notas foram criadas, quantas receberam cada tag de pendência, e lista os termos não resolvidos

#### Scenario: Anomalias listadas

- **WHEN** notas recebem a tag `video-suspeito` ou `grupo-misto`
- **THEN** o relatório lista as palavras afetadas para conferência manual
