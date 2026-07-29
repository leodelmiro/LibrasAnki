## Why

Estou aprendendo LIBRAS e preciso de um baralho Anki alimentado pelo Dicionário da Língua Brasileira de Sinais do INES (`dicionario.ines.gov.br`), montado a partir das palavras e frases que aparecem nas minhas aulas.

A investigação do site mostrou que o dicionário inteiro está exposto em um único arquivo JavaScript (`public/site/js/palavras.js`, ~2 MB, 5.826 verbetes com vídeo em MP4). Isso torna a coleta trivial — mas também revelou que os dados **não** podem ser convertidos em cards ingenuamente:

- 80% dos verbetes com sufixo numérico (`ABANDONAR1`/`ABANDONAR2`) são **homônimos com sentidos distintos**, não variantes do mesmo sinal. Juntá-los ensinaria o sinal errado.
- Existem erros na base: `DOIS2` aparece duas linhas com o mesmo `ident` e uma delas aponta para o vídeo de `DOAR2`. Outros 16 vídeos são compartilhados entre dois verbetes.
- Boa parte do meu material de aula **não existe** no dicionário: saudações compostas (`BOM DIA`, `BOA TARDE`, `BOA NOITE`), `TERÇA-FEIRA`, `ATRASADO`, e a distinção morfológica ordinal/cardinal/quantidade que a aula ensina.

Uma fonte secundária (Spread the Sign) foi avaliada e **descartada**: cobre só 7 das lacunas, proíbe download de vídeos, e não resolve as saudações compostas — que faltam nos dois dicionários porque são compostas em tempo real, não itens de léxico.

Portanto a ferramenta precisa tratar o INES como fonte parcial e imperfeita, e me dar um caminho explícito para completar o resto à mão.

## What Changes

- Nova ferramenta de linha de comando que lê listas de estudo e produz um arquivo `.apkg` importável no Anki (desktop e AnkiMobile).
- Coleta e cache local do dataset do INES a partir do `palavras.js`, com download dos MP4 apenas das palavras solicitadas.
- Busca tolerante a acento, caixa e flexão verbal simples (`cheguei` → `CHEGAR`, `vou` → `IR`), já que as listas vêm escritas em português corrente.
- Classificação automática de grupos com sufixo numérico em **variante** (mesma `descricao` + mesma `classe` → um card com múltiplos vídeos) ou **homônimo** (cards separados, cada um com sua descrição).
- Detecção e marcação de anomalias conhecidas da base (`ident` duplicado, vídeo compartilhado entre verbetes não relacionados).
- Geração de **uma nota por sinal com três templates de card**: recepção (vídeo → palavra), produção (palavra → vídeo) e gramática (frase em português ↔ glosa em LIBRAS).
- GUID estável derivado de `ident` + nome do vídeo, permitindo regerar e reimportar o baralho sem duplicar cards nem perder histórico de revisão.
- Palavras e frases sem material no INES **nunca são puladas em silêncio**: viram cards marcados (`falta-video`, `falta-glosa`) para preenchimento manual.

**Fora de escopo:** fonte de dados secundária, gravação/edição de vídeo, sincronização com AnkiWeb, interface gráfica.

## Capabilities

### New Capabilities

- `dicionario-ines`: obter, cachear e consultar o dataset do INES — download do `palavras.js` e dos MP4, normalização, busca tolerante, resolução variante/homônimo e marcação de anomalias da base.
- `geracao-baralho`: construir o pacote Anki — modelo de nota, os três templates de card, GUID estável, embutir mídia e escrever o `.apkg`.
- `listas-de-estudo`: formato das listas de entrada (palavras e frases), resolução contra o dicionário, e o fluxo de completar manualmente o que falta.

### Modified Capabilities

Nenhuma — o projeto não tem specs existentes.

## Impact

- Projeto Python novo, atualmente vazio (só `.venv` com pip). Nenhum código existente é afetado.
- Dependências novas: `genanki` (geração do `.apkg`), `requests` (download) e `imageio-ffmpeg` (converte os MP4 para WebM, único formato que o webview do Anki desktop decodifica — ver decisão 8 do design). Sem framework web, sem banco de dados.
- Rede: acesso a `dicionario.ines.gov.br`. Um download de ~2 MB do dataset (cacheado) e ~30–50 KB por vídeo solicitado.
- Artefatos em disco: cache do dataset, dos vídeos originais e das conversões WebM, listas de estudo versionáveis, e o `.apkg` gerado. Cada sinal ocupa ~50 KB no pacote por levar os dois formatos.
