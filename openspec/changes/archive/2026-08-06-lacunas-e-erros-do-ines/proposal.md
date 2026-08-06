## Why

Investigar por que certos cards estavam sem vídeo revelou que "sem vídeo" escondia quatro situações diferentes, tratadas como se fossem a mesma:

1. **O INES declara vídeo que o servidor não entrega.** `FEMININO`, `DORMIR`, `PESSOA1` e `VOVÓ-VOVÔ` têm verbete, com nome de arquivo preenchido, e o download responde 404. Não é lacuna de dicionário, é link quebrado — e num dos casos o próprio INES mostra o mesmo sinal em outra entrada: `FEMININO` é o sinal de `MULHER`, cujo vídeo baixa normalmente.
2. **A palavra não existe na língua, não no dicionário.** `TEU` e `TUA` são transporte do português: em LIBRAS o possessivo de 2ª pessoa é `SEU`. O card dizia "sem verbete no INES, preencher com material da aula", o que sugeria uma gravação que nunca vai existir, porque o sinal certo é outro e já está no baralho.
3. **O composto estava errado.** `FIM DE SEMANA` era montado como `FIM` + `SEMANA`, tradução literal do português. Em LIBRAS se nomeia os dois dias: `SÁBADO` + `DOMINGO`. O mesmo defeito estava dentro de `tenha um bom fim de semana`.
4. **Card espúrio por colisão de normalização.** Pedir `carne` gerava dois cards, porque a normalização tira o acento e `CARNÊ` (bloco de pagamento) vira a mesma chave de `CARNE` (o alimento). Dois cards com descrições sem relação nenhuma, um deles fora do currículo.

Nada disso é o mesmo problema, e nenhum deles se resolve gravando na aula.

## What Changes

- **`MESMO_SINAL`**: quando o vídeo próprio de um verbete não é obtido e outro verbete tem o mesmo sinal, a nota usa o vídeo do irmão, com a tag `mesmo-sinal` e a observação dizendo de onde veio. `FEMININO` passa a mostrar o vídeo de `MULHER`.
- **`CORRECOES`**: formas que não existem em LIBRAS ganham um conceito próprio, separado de "lacuna do dicionário". O card mostra o vídeo do sinal correto e leva a tag `forma-incorreta`. `teu` e `tua` apontam para `SEU`.
- **`NOTAS_DE_SINAL`**: observações presas a um sinal, para o que o verbete não diz sozinho. `VOVÓ-VOVÔ` passa a explicar que é um sinal só para os dois avós, marcado com o feminino.
- **`IGNORADOS`**: verbetes retirados do índice quando a normalização os cola em outro de sentido sem relação. `CARNÊ` sai; `carne` volta a gerar um card só.
- **`COMPOSTOS`**: `fim de semana` entra como `SÁBADO` + `DOMINGO`, e `tenha um bom fim de semana` é corrigido para `BOM` + `SÁBADO` + `DOMINGO`.
- Dois blocos novos no relatório: `FORMA INCORRETA` e `VÍDEO EMPRESTADO`.

**Fora de escopo:** varrer a base atrás de todos os 404 e de todas as colisões de normalização. As quatro tabelas são declarativas e crescem quando um caso aparece nas aulas, como já acontece com `COMPOSTOS`.

## Capabilities

> **Ordem de arquivamento: antes de `videos-de-fora-do-ines`.** As duas changes
> modificam os mesmos três requisitos, e um delta `MODIFIED` substitui o
> requisito inteiro. Os deltas da outra já incluem o que esta acrescenta, então
> esta vai primeiro.

### Modified Capabilities

- `dicionario-ines`: a busca passa a admitir verbetes excluídos do índice por colisão de normalização. O download de vídeo passa a admitir uma alternativa antes de a nota cair em `falta-video`.
- `listas-de-estudo`: o requisito "Pendências viram tags, nunca omissão" passa a distinguir a forma que não existe na língua — que recebe `forma-incorreta` e o vídeo do sinal correto — do item que de fato não tem material.
- `geracao-baralho`: o relatório passa a listar as correções aplicadas e os vídeos emprestados, para que as quatro tabelas sejam revisáveis sem abrir o Anki.

## Impact

**Código**
- `libras_anki/indice.py`: `IGNORADOS` filtra `self.verbetes` na construção do `Indice`, antes da montagem dos dois dicionários de busca. Distinto de `FALSOS_AMIGOS`, que bloqueia o termo inteiro; aqui o termo resolve normalmente e só o verbete indesejado sai.
- `libras_anki/gerador.py`: `MESMO_SINAL`, `CORRECOES` (com o namedtuple `Correcao`) e `NOTAS_DE_SINAL` novos; `_nota_de_sinal` ganha o degrau de empréstimo e a observação por sinal; `_nota_ausente` trata correção ao lado de composto; `Relatorio` ganha `correcoes` e `mesmo_sinal`.
- `libras_anki/gerador.py`: entrada `fim de semana` em `COMPOSTOS` e correção de `tenha um bom fim de semana`.

**Conteúdo**
- `README.md`: tags `forma-incorreta` e `mesmo-sinal` na tabela.
- `listas/dias-da-semana.txt`, `listas/pronomes-possessivos.txt`, `listas/vocabulario-diverso.txt`, `listas/familia.txt`: comentários que afirmavam lacuna onde não havia, ou descreviam configuração de mão para um sinal que não existe.

**Baralho existente**
- `CARNÊ` deixa de ser gerado: uma nota a menos. É a única nota que desaparece, e some porque não deveria existir.
- `teu`, `tua` e `feminino` mantêm o GUID e ganham vídeo na reimportação, com o histórico preservado.
- `fim de semana` e `tenha um bom fim de semana` mantêm o GUID e trocam os vídeos dos componentes.

**Sem impacto**
- Dependências, modelos de nota, formato do `.apkg`, e o caminho de qualquer palavra fora das quatro tabelas.
