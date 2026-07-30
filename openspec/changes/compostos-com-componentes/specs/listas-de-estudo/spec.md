## MODIFIED Requirements

### Requirement: Pendências viram tags, nunca omissão

O sistema MUST NOT descartar em silêncio nenhum item das listas. Todo item sem material completo MUST gerar nota marcada para preenchimento manual.

Itens compostos — que não têm verbete próprio porque se sinalizam em sequência — MUST ser montados a partir dos vídeos dos componentes quando estes existirem no dicionário, e MUST receber a tag `composto`. Nesse caso o sistema MUST NOT aplicar `falta-video`, porque não há nada a gravar para o card funcionar.

Quando a escolha de um componente resultar de eliminação entre homônimos, e não de conhecimento confirmado, a nota MUST receber a tag `confirmar-sinal` e o card MUST dizer o que precisa ser checado.

#### Scenario: Palavra sem verbete

- **WHEN** uma palavra da lista não é resolvida contra o dicionário e não é um composto conhecido
- **THEN** uma nota é criada com a tag `falta-video` em vez de o item ser omitido

#### Scenario: Filtragem no Anki

- **WHEN** o usuário busca por `tag:falta-video` no Anki
- **THEN** obtém a lista do que precisa completar com material das aulas

#### Scenario: Composto com componentes disponíveis

- **WHEN** um item da lista é um composto conhecido e seus componentes têm vídeo no INES
- **THEN** o card mostra os vídeos dos componentes em sequência, cada um rotulado com o nome do sinal, e a nota recebe `composto` sem receber `falta-video`

#### Scenario: Composto com escolha de homônimo

- **WHEN** um componente foi escolhido por eliminação entre homônimos de sentidos diferentes
- **THEN** a nota recebe `confirmar-sinal` e a observação do card nomeia o que confirmar na aula

#### Scenario: Componente sem vídeo

- **WHEN** um componente declarado não é encontrado ou não tem vídeo
- **THEN** o card informa qual componente ficou de fora, em vez de omiti-lo silenciosamente

#### Scenario: Composto sem nenhum componente disponível

- **WHEN** nenhum componente de um composto pôde ser resolvido
- **THEN** a nota recebe `falta-video`, como qualquer item sem material
