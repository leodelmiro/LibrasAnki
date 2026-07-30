## Why

`BOA TARDE` não existe como verbete no INES porque se sinaliza BOA + TARDE em sequência. Hoje esses itens viram um card sem vídeo nenhum, com a tag `falta-video` e um aviso mandando gravar na aula — mas os componentes **existem no dicionário**, com vídeo. O card está vazio por construção, não por falta de material.

São 6 itens nessa situação (`bom dia`, `boa tarde`, `boa noite`, `de nada`, `até amanhã`, `tenha um bom fim de semana`), todos cumprimentos de uso diário — justamente o que se pratica primeiro numa aula de LIBRAS.

A investigação para montar isso revelou um bug independente: **`dia` e `bolo` eram inalcançáveis na busca**. O INES escreve `DIA 1`, `DIA 2` com espaço antes do número, e `raiz()` só removia dígitos colados (`ABANDONAR2`), deixando `"DIA "` com espaço sobrando. O mesmo defeito partia `MAIS` e `REDE` — que misturam os dois padrões — em dois grupos quando são um sinal só.

## What Changes

- Compostos passam a mostrar os vídeos dos componentes em sequência, rotulados, no lugar do card vazio.
- Os componentes são **declarados explicitamente** por nome de verbete, não derivados de dividir a string em palavras. Sem isso não dá para tratar palavra funcional sem sinal (`de`, `tenha`) nem escolher entre homônimos — `BOM` tem 3 sentidos no INES e `BOA` tem 2, e a resolução automática pegaria o primeiro no escuro.
- Duas tags novas: `composto` (item sem verbete próprio, sinalizado em sequência) e `confirmar-sinal` (a escolha do componente saiu por eliminação a partir da descrição do INES, não de conhecimento confirmado).
- Compostos com componentes resolvidos **deixam de receber `falta-video`**: há o que praticar hoje, nada precisa ser gravado para o card funcionar. A tag cai de 25 para 19 notas.
- Bloco `COMPOSTOS` no relatório, listando como cada um foi montado.
- Correção de `raiz()` para tolerar o espaço antes do sufixo numérico.

**Fora de escopo:** inferir componentes automaticamente, adicionar compostos além dos 6 já mapeados, e qualquer fonte de sinal fora do INES.

## Capabilities

### New Capabilities

Nenhuma — a mudança altera comportamento já especificado.

### Modified Capabilities

- `listas-de-estudo`: o requisito "Pendências viram tags, nunca omissão" passa a distinguir dois casos. Item sem material nenhum continua com `falta-video`; composto cujos componentes têm vídeo recebe `composto` e é montado a partir deles.
- `dicionario-ines`: o requisito "Busca tolerante a acento, caixa e flexão" passa a exigir que a remoção do sufixo numérico tolere espaço antes do número.
- `geracao-baralho`: o requisito "Modelo de nota por tipo de item" ganha a possibilidade de a nota de palavra carregar vídeos de componentes rotulados em vez do vídeo de um sinal próprio.

## Impact

**Código**
- `libras_anki/indice.py`: `_SUFIXO_NUMERICO` passa de `\d+$` para `\s*\d+$`. Afeta `raiz()`, usada tanto na busca quanto no agrupamento de `grupos.classificar`.
- `libras_anki/gerador.py`: `COMPOSTOS` deixa de ser `str -> str` e passa a `str -> Composto(nota, sinais, confirmar)`; novo método `_componentes`; `_nota_ausente` monta os vídeos; `Relatorio` ganha a lista `compostos`.
- `libras_anki/modelo.py`: `criar_nota` aceita `componentes`, usando `html_vocabulario` (rótulo por componente) em vez de `html_videos` (rotula como "variante 1, 2…"), porque componentes não são variantes de um mesmo sinal.

**Conteúdo**
- `README.md`: seção "Compostos" e as duas tags novas na tabela.
- `listas/saudacoes.txt`: o comentário dizia que esses itens ficam com `falta-video`, o que deixou de ser verdade.

**Baralho existente**
- Os 6 compostos mantêm o GUID (derivado de `ausente:<texto>`), então são atualizados na reimportação sem perder histórico — ganham vídeo onde antes havia só o aviso.
- O agrupamento de `MAIS` e `REDE` muda com a correção de `raiz()`, mas nenhum deles está nas listas atuais, então o baralho gerado não muda: 123 notas antes e depois.

**Sem impacto**
- Dependências, rede além dos vídeos dos componentes (12 arquivos novos em cache), formato do `.apkg`.
