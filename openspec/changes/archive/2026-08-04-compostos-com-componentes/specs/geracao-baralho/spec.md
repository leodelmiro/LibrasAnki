## MODIFIED Requirements

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

### Requirement: Relatório de execução

O sistema MUST emitir, ao final da geração, um resumo das notas criadas e de tudo que exigiu atenção. O relatório MUST NOT conter seção de glosa pendente. O relatório MUST listar como cada composto foi montado, para que a escolha dos componentes seja revisável sem abrir o Anki.

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
