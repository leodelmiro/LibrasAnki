## MODIFIED Requirements

### Requirement: Pendências viram tags, nunca omissão

O sistema MUST NOT descartar em silêncio nenhum item das listas. Todo item sem material completo MUST gerar nota marcada para preenchimento manual.

O sistema MUST distinguir a forma que não existe em LIBRAS do item que não tem material. Uma forma que é transporte do português — cuja tradução correta é outro sinal que o dicionário tem — MUST gerar card mostrando o vídeo do sinal correto, MUST receber a tag `forma-incorreta`, e MUST NOT receber `falta-video`. O card MUST continuar existindo com a palavra incorreta na frente: é ele que desfaz o engano de quem vem do português.

Itens compostos — que não têm verbete próprio porque se sinalizam em sequência — MUST ser montados a partir dos vídeos dos componentes quando estes existirem no dicionário, e MUST receber a tag `composto`. Nesse caso o sistema MUST NOT aplicar `falta-video`, porque não há nada a gravar para o card funcionar.

Os componentes de um composto MUST refletir como a expressão se sinaliza, e não a tradução palavra por palavra do português. Um composto montado por tradução literal produz um card que parece completo e ensina uma sequência inexistente, o que é pior que um card vazio.

Quando a escolha de um componente resultar de eliminação entre homônimos, e não de conhecimento confirmado, a nota MUST receber a tag `confirmar-sinal` e o card MUST dizer o que precisa ser checado.

#### Scenario: Palavra sem verbete

- **WHEN** uma palavra da lista não é resolvida contra o dicionário, não é um composto conhecido e não é forma incorreta conhecida
- **THEN** uma nota é criada com a tag `falta-video` em vez de o item ser omitido

#### Scenario: Filtragem no Anki

- **WHEN** o usuário busca por `tag:falta-video` no Anki
- **THEN** obtém a lista do que precisa completar com material das aulas

#### Scenario: Forma que não existe em LIBRAS

- **WHEN** um item da lista é transporte do português cuja forma correta é outro sinal do dicionário
- **THEN** o card mostra o vídeo do sinal correto, a observação diz qual é e por quê, e a nota recebe `forma-incorreta` sem receber `falta-video`

#### Scenario: Composto com componentes disponíveis

- **WHEN** um item da lista é um composto conhecido e seus componentes têm vídeo no INES
- **THEN** o card mostra os vídeos dos componentes em sequência, cada um rotulado com o nome do sinal, e a nota recebe `composto` sem receber `falta-video`

#### Scenario: Composto que não é tradução literal

- **WHEN** a expressão se sinaliza de forma diferente da sequência das palavras em português
- **THEN** os componentes declarados são os do sinal real, e não os das palavras traduzidas uma a uma

#### Scenario: Composto com escolha de homônimo

- **WHEN** um componente foi escolhido por eliminação entre homônimos de sentidos diferentes
- **THEN** a nota recebe `confirmar-sinal` e a observação do card nomeia o que confirmar na aula

#### Scenario: Componente sem vídeo

- **WHEN** um componente declarado não é encontrado ou não tem vídeo
- **THEN** o card informa qual componente ficou de fora, em vez de omiti-lo silenciosamente

#### Scenario: Composto sem nenhum componente disponível

- **WHEN** nenhum componente de um composto pôde ser resolvido
- **THEN** a nota recebe `falta-video`, como qualquer item sem material
