## ADDED Requirements

### Requirement: Declaração de vídeo externo na lista de estudo

Uma linha de lista MUST poder apontar um vídeo de fora do INES para o seu item, com o marcador `@yt` seguido de uma URL e, opcionalmente, de um trecho. O sistema MUST separar essa declaração do texto do item antes de decidir se a linha é palavra ou frase, para que a URL não conte como palavra significativa.

O trecho MUST aceitar `início-fim` e `início+duração`, com tempos em `M:SS`, `H:MM:SS` ou segundos, com decimais opcionais. Sem trecho, o clipe MUST ser o vídeo inteiro.

O sistema MUST NOT interromper a geração por causa de uma declaração malformada. A linha MUST virar card sem o vídeo, e o problema MUST ser reportado com o arquivo e o número da linha.

#### Scenario: Palavra com trecho declarado

- **WHEN** uma linha traz `terça-feira @yt https://youtu.be/AAA 1:23-1:27`
- **THEN** o item é a palavra "terça-feira" e o vídeo externo aponta para o trecho de 83s a 87s daquela URL

#### Scenario: Trecho por duração

- **WHEN** o trecho é escrito como `0:41+3`
- **THEN** o clipe vai de 41s a 44s

#### Scenario: Link sem trecho

- **WHEN** a linha traz apenas a URL, sem trecho
- **THEN** o vídeo inteiro vira o clipe

#### Scenario: URL malformada

- **WHEN** o que segue o `@yt` não é uma URL, ou o fim vem antes do início
- **THEN** o card é gerado sem o vídeo externo e o relatório registra a origem, a linha e o motivo

### Requirement: Obtenção, recorte e cache do vídeo externo

O sistema MUST baixar cada URL declarada uma única vez, mantendo o arquivo completo em cache, e MUST recortar cada clipe a partir desse arquivo. Dois itens que apontem para o mesmo trecho da mesma URL MUST compartilhar o mesmo clipe.

O recorte MUST reencodar o vídeo, e o sistema MUST NOT cortar por cópia de fluxo, porque o corte sem reencode só cai em keyframe e o erro resultante é da ordem de grandeza da duração de um sinal.

O sistema MUST produzir os dois formatos usados pelo baralho — WebM/VP9 e MP4/H.264 — e MUST limitar a largura do clipe, já que a fonte é muito maior que os vídeos do INES.

#### Scenario: Vídeo reaproveitado entre itens

- **WHEN** duas linhas declaram trechos diferentes da mesma URL
- **THEN** a URL é baixada uma vez e cada trecho é recortado do arquivo em cache

#### Scenario: Clipe já em cache

- **WHEN** os dois formatos de um clipe já existem em cache
- **THEN** nem o download nem o recorte são refeitos

#### Scenario: Falha de download

- **WHEN** o download de uma URL falha
- **THEN** a nota é gerada sem o vídeo externo, mantendo o que já teria, e a falha é registrada no relatório com o motivo

#### Scenario: Vídeo público recusado pelo client padrão

- **WHEN** o client padrão responde que o vídeo não está disponível
- **THEN** o sistema tenta os demais clients configurados antes de considerar o download falho

### Requirement: Aviso de clipe longo demais para um sinal

O sistema MUST avisar quando um clipe pronto ultrapassar a duração plausível de um sinal, para expor o caso de um vídeo inteiro ter entrado no baralho por esquecimento do trecho. A duração MUST ser medida no arquivo gerado, e o sistema MUST NOT avisar apenas por ausência de trecho na declaração.

#### Scenario: Link curto sem trecho

- **WHEN** uma linha declara um link sem trecho e o vídeo tem poucos segundos
- **THEN** nenhum aviso é emitido

#### Scenario: Vídeo inteiro entrando por esquecimento

- **WHEN** o clipe gerado ultrapassa o limite de duração
- **THEN** o relatório lista o link e a duração medida
