## MODIFIED Requirements

### Requirement: Relatório de execução

O sistema MUST emitir, ao final da geração, um resumo das notas criadas e de tudo que exigiu atenção. O relatório MUST NOT conter seção de glosa pendente. O relatório MUST listar como cada composto foi montado, para que a escolha dos componentes seja revisável sem abrir o Anki.

O relatório MUST listar as formas incorretas com o sinal que as substituiu, e os vídeos emprestados com o verbete de origem. As tabelas que decidem esses dois casos são mantidas à mão, e o relatório é onde elas ficam auditáveis: quando um verbete deixar de aparecer no bloco de vídeo emprestado, a entrada correspondente pode sair da tabela.

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
