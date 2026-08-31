## Why

O verso da frase montava o vocabulário palavra por palavra, e essa quebra tinha dois defeitos que só apareciam quando alguém ia estudar. Uma expressão de várias palavras que é **um sinal só** se perdia nos pedaços: "por que" caía pela metade nas palavras funcionais e o "por" restante era falso amigo (`PÔR`, o verbo colocar); "o que" sumia inteiro, sendo as duas funcionais; "mais ou menos" resolvia como `MAIS 1` + `OU` + `MENOS1`, três sinais sem relação nenhuma com aproximação.

E quando o INES tinha mais de um sinal para a palavra, o gerador pegava o primeiro verbete sem ter como saber se era o certo. Para "qual" isso dava o sentido de identificar um *local*, na frase do prato mais famoso; para "quem", o de identificar o *proprietário de um objeto*, em "Quem mora com você?". O card parecia completo e ensinava o sinal errado — exatamente o que o projeto evita em todo o resto.

## What Changes

- Tabela `EXPRESSOES` em `indice.py`: sequências de palavras que são um sinal só, reconhecidas **antes** de a frase ser quebrada em palavras. `por que` → `PORQUE`, `o que` → `QUE`, `mais ou menos` → a expressão inteira. O casamento é do maior para o menor, para que uma expressão que comece igual a outra não seja partida pela mais curta.
- O verso da frase **mostra todos os sentidos** quando o INES tem mais de um sinal para a palavra, lado a lado e rotulados pela descrição do dicionário. Quem escolhe é quem está sinalizando, que é quem sabe. A nota recebe a tag `escolher-sentido` e a observação nomeia as palavras com opção.
- Variantes MUST NOT virar opção de escolha: `MEU1`/`MEU2` e `FOLGA1`/`FOLGA2` têm a mesma descrição, são o mesmo sinal em dois verbetes, e continuam mostrando um vídeo só. A contagem é de sinais, não de verbetes.
- Bloco `ESCOLHA NO VERSO` no relatório, listando cada frase e as palavras que oferecem escolha.
- Observação do card ausente deixa de mandar "preencher com material da aula" quando o card já tem clipe de fora — a instrução contradizia o próprio card.
- `kg` entra em `NOTAS_DE_LINGUA`: não é lacuna do dicionário, é abreviatura, e se soletra K + G.

**Fora de escopo:** fixar qual sentido cada frase usa. Uma tabela `(frase, palavra) → verbete` resolveria o card sem pedir nada ao estudante, mas exige conhecimento de LIBRAS que o dicionário não dá — a descrição do INES diz que a escolha automática está errada, não qual é a certa. Mostrar as opções é a resposta honesta enquanto esse conhecimento não estiver declarado.

## Capabilities

### Modified Capabilities

- `listas-de-estudo`: o requisito dos cards de frase passa a definir o que acontece quando uma palavra tem mais de um sinal, e a reconhecer expressões de várias palavras como um item só do vocabulário.
- `dicionario-ines`: o requisito de busca tolerante ganha o casamento de sequências de palavras, aplicado antes do descarte das palavras funcionais.
- `geracao-baralho`: o requisito de relatório passa a listar as frases que oferecem escolha de sentido.

## Impact

**Código**
- `libras_anki/indice.py`: `EXPRESSOES` e `_MAIOR_EXPRESSAO`; `palavras_da_frase` casa sequências do maior para o menor antes de aplicar `VAZIAS`.
- `libras_anki/gerador.py`: `_sinais_de` devolve os sinais distintos de uma resolução; `_rotulo_de_sentido` monta o rótulo com a descrição do INES; `TAG_ESCOLHER_SENTIDO`; `_nota_frase` emite um bloco por sentido; `Relatorio.escolha_de_sentido` e o bloco novo; `NOTAS_DE_LINGUA` ganha `kg`.

**Conteúdo**
- `README.md`: a seção de frases descreve a escolha de sentido, e a tabela de tags ganha `escolher-sentido`.
- `listas/frases-apostila.txt`, `listas/frases-perguntas.txt`, `listas/frases-pronomes.txt`: comentários de cobertura reescritos — os que listavam "Libras", "Por", "kg" e "média" como buracos deixaram de valer.
- `listas/frases-pronomes.txt`: a frase do kg de carne passa a perguntar "mais ou menos" em vez de "em média", que é a expressão usada em LIBRAS.

**Baralho existente**
- Nenhum modelo de nota muda; a reimportação atualiza no lugar.
- **BREAKING:** o GUID da nota de frase deriva do texto em português, então trocar "em média" por "mais ou menos" cria nota nova e deixa a antiga órfã no Anki de quem já importou. Precisa ser apagada à mão no navegador.
- 22 das 38 frases passam a levar `escolher-sentido`. As frases que avisavam "sem sinal no INES" caem de 15 para 1 — sobra "Lulu", nome próprio, que se faz por datilologia.

**Sem impacto**
- Cards de palavra, de número e de composto. A escolha de sentido vale só para o vocabulário do verso da frase; homônimos continuam virando um card cada, como já era.
