## RENAMED Requirements

- FROM: `### Requirement: Modelo de nota único com três templates`
- TO: `### Requirement: Modelo de nota por tipo de item`

## MODIFIED Requirements

### Requirement: Modelo de nota por tipo de item

O sistema MUST gerar uma nota por sinal, com os templates de card determinados pelo tipo do item. Palavras MUST ter dois templates — recepção e produção. Frases MUST ter um único template — sinalizar. O sistema MUST NOT gerar card de gramática em nenhum dos modelos: o baralho pratica sinais, não notação escrita.

A nota de palavra MUST conter apenas os campos `Palavra`, `Videos`, `Descricao`, `Origem` e `Observacao`. O sistema MUST NOT incluir exemplo, glosa, configuração de mão nem classe gramatical na nota de palavra.

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

### Requirement: Reprodução de vídeo em desktop e AnkiMobile

O sistema MUST embutir os vídeos usando um elemento `<video>` com os atributos `autoplay`, `loop`, `muted` e `playsinline`, contendo dois elementos `<source>`: WebM primeiro, MP4 em seguida. O webview do Anki desktop não decodifica H.264 e o WebKit do iOS não decodifica WebM em versões mais antigas, então cada plataforma seleciona o formato que sabe reproduzir.

Quando não houver vídeo disponível, o sistema MUST escrever um aviso no lugar do elemento `<video>`, dentro do mesmo campo, de modo que o card continue sendo gerado.

#### Scenario: Revisão no Anki desktop

- **WHEN** um card com vídeo é revisado no Anki desktop
- **THEN** o vídeo WebM é reproduzido dentro do card

#### Scenario: Revisão no AnkiMobile

- **WHEN** um card com vídeo é revisado no AnkiMobile
- **THEN** o vídeo MP4 é reproduzido dentro do card

#### Scenario: Sinal sem vídeo disponível

- **WHEN** um sinal não tem vídeo no INES ou o download falhou
- **THEN** o campo de vídeo contém um aviso legível no lugar do elemento `<video>`, e tanto o card de recepção quanto o de produção continuam sendo gerados

### Requirement: Relatório de execução

O sistema MUST emitir, ao final da geração, um resumo das notas criadas e de tudo que exigiu atenção. O relatório MUST NOT conter seção de glosa pendente.

#### Scenario: Resumo ao final

- **WHEN** a geração termina
- **THEN** o relatório informa quantas notas foram criadas, quantas receberam cada tag de pendência, e lista os termos não resolvidos

#### Scenario: Anomalias listadas

- **WHEN** notas recebem a tag `video-suspeito` ou `grupo-misto`
- **THEN** o relatório lista as palavras afetadas para conferência manual

#### Scenario: Sem bloco de glosa

- **WHEN** o relatório é emitido
- **THEN** nenhum bloco "SEM GLOSA" é impresso, porque a glosa deixou de fazer parte do baralho
