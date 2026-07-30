## Why

O baralho existe para ensinar **sinais**, não notação escrita. A glosa é uma convenção de transcrição usada por quem estuda linguística de LIBRAS — ela não é o que se pratica numa conversa, e cada frase pendente de glosa criava uma dívida com a professora antes de o card virar útil.

O card de palavra já foi simplificado nessa direção (commit `51168da`): saíram Exemplo, Glosa, Mão e Classe. Falta fazer o mesmo nas frases, onde a glosa continua inteira — campo, card de gramática, tag `falta-glosa` e a sintaxe `|` das listas. Enquanto isso as specs de `libras-anki-deck` ainda descrevem o modelo antigo de três templates, então código e spec divergiram.

Separadamente, a investigação do VLibras (23.432 sinais, contra 5.824 do INES) mostrou que várias lacunas que o projeto afirma serem inexistentes "em dicionário nenhum" — `BOM_DIA`, `TERÇA_FEIRA`, `LIBRAS`, `TEU`, `TUA`, `VOSSO`, `VOSSA`, `FIM_DE_SEMANA` — existem lá como sinal catalogado. A afirmação atual ficou maior que a evidência.

## What Changes

- **BREAKING** Remoção da glosa do modelo de frase: some o campo `Glosa`, some o card de gramática, e `MODELO_FRASE` passa a ter **um único card** ("Sinalize esta frase" → vídeos do vocabulário no verso).
- **BREAKING** A sintaxe `separador |` das listas de estudo deixa de existir. Linhas que hoje trazem `frase | GLOSA` passam a ser lidas como frase simples.
- Remoção da tag `falta-glosa`, do bloco "SEM GLOSA" do relatório e do contador correspondente.
- Alinhamento das specs com o modelo de palavra já implementado: dois templates (recepção e produção), sem Exemplo, Glosa, Mão nem Classe; e o aviso de vídeo ausente embutido no campo `Videos`, o que faz o card de recepção continuar existindo quando não há vídeo.
- Correção das afirmações sobre lacunas: o que foi verificado é que INES e Spread the Sign não têm esses verbetes — não que "não existem em dicionário nenhum". O VLibras registra vários deles.
- **Não muda**: o modelo de palavra (já implementado), os cards de número/contraste, o GUID estável, a conversão WebM, e o princípio de que nada é descartado em silêncio.

## Capabilities

### New Capabilities

Nenhuma — a mudança altera comportamento já especificado.

### Modified Capabilities

- `geracao-baralho`: o requisito "Modelo de nota único com três templates" passa a descrever dois templates para palavra e um para frase; o card de gramática deixa de existir em ambos os modelos. O comportamento de vídeo ausente passa a ser "aviso dentro do campo `Videos`" em vez de supressão do card de recepção.
- `listas-de-estudo`: o requisito "Cards de frase com glosa pendente" perde a glosa por completo — não há mais tag `falta-glosa`, sintaxe `|`, nem card de gramática. O requisito "Listas de estudo em arquivos de texto" perde a glosa como sinal de tipo na interpretação das linhas.

## Impact

**Código**
- `libras_anki/modelo.py`: `CAMPOS_FRASE` perde `Glosa`; `TEMPLATES_FRASE` perde o template `Gramatica`; `criar_nota_frase` perde o parâmetro; CSS `.glosa` fica órfão.
- `libras_anki/gerador.py`: `TAG_FALTA_GLOSA`, `Relatorio.falta_glosa` e o bloco "SEM GLOSA" saem; `_nota_frase` para de ler `item.glosa`.
- `libras_anki/listas.py`: `SEPARADOR_GLOSA`, o atributo `Item.glosa` e o ramo de interpretação que usa a glosa para decidir o tipo da linha saem. **Ponto de atenção**: hoje a presença do `|` decide que a linha é frase *antes* de consultar o dicionário; sem ele essas linhas passam a depender da heurística seguinte (resolve no INES → palavra; mais de uma palavra significativa → frase).

**Conteúdo**
- `listas/frases-apostila.txt` e `listas/frases-pronomes.txt`: cabeçalhos que documentam a sintaxe `|` ficam obsoletos.
- `listas/saudacoes.txt` e `listas/dias-da-semana.txt`: afirmações sobre lacunas a corrigir.
- `README.md`: tabela de formato das linhas, tabela de tags, seção "O que o baralho tem".

**Baralho existente**
- Notas de frase já importadas no Anki mantêm o GUID (derivado do texto em português), então são atualizadas em vez de duplicadas. Os cards de gramática de frase que já existirem no Anki ficam órfãos e precisam ser removidos manualmente — o Anki não apaga cards ao remover um template na reimportação.

**Sem impacto**
- Dependências, rede, cache, formato do `.apkg`.
