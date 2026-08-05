## Why

O baralho tinha uma resposta só para "não tem vídeo": o aviso "Sem vídeo disponível — grave na aula". Isso funciona para o que a professora vai mostrar na próxima aula, mas não para lacunas que ninguém vai preencher tão cedo — `TERÇA-FEIRA`, `TELEFONE`, `PAMONHA`, `TIA` não existem no INES e não é a aula que vai fazê-los existir.

Enquanto isso, o sinal está em vídeo em canais de LIBRAS no YouTube, aberto, a um link de distância. O card ficava esperando uma gravação que já existia em outro lugar.

Há um segundo caso, diferente do primeiro: a palavra tem vídeo no INES e mesmo assim você prefere outro — variante regional, vídeo do INES ruim, sinal que a professora faz de outro jeito. Aí não é lacuna, é escolha, e o baralho não tinha como registrá-la.

## What Changes

- As linhas das listas aceitam `@yt <url> [trecho]`, apontando um vídeo de fora para aquele item. O trecho é `início-fim` ou `início+duração`, em `M:SS`, `H:MM:SS` ou segundos; sem trecho, o vídeo inteiro vira o clipe.
- O vídeo é baixado com `yt-dlp`, recortado com ffmpeg e convertido para o mesmo par de formatos dos vídeos do INES — WebM/VP9 e MP4/H.264 — porque a razão é a mesma: o webview do desktop não decodifica H.264 e o iOS não decodifica WebM.
- **O link tem prioridade sobre o INES.** Numa palavra que o dicionário já cobre, o clipe de fora substitui o vídeo do INES no card. Quem foi atrás de outro vídeo quis outro vídeo; o card registra a troca na observação e leva a tag `video-externo`.
- Vale para palavra, para item sem verbete e para frase. Na frase o clipe vai no topo do verso, rotulado "a frase sinalizada", antes dos vídeos do vocabulário — a frase inteira mostra a ordem e o encadeamento, que é o que o card pede.
- O vídeo é baixado inteiro uma vez para `.cache/externos/` e recortado dali. Um vídeo de aula de dez minutos serve dezenas de sinais pagando um download só.
- Falha de download não derruba nada: o card volta ao que era — vídeo do INES, ou o aviso de lacuna — e a falha vai para o relatório com o motivo. Linha com `@yt` malformado vira card normal, com o problema reportado em `arquivo:linha`.
- Três blocos novos no relatório: `PROBLEMAS NAS LISTAS`, `VÍDEO EXTERNO FALHOU` e `CLIPE LONGO` (clipe pronto acima de 30s, medido no arquivo — sinal nenhum dura isso).
- 10 links escritos nas listas, cobrindo `terça-feira`, `tia`, `vô`, `vosso`, `vossa`, `ótimo`, `dormir`, `pessoa`, `telefone` e `pamonha`.

**Fora de escopo:** buscar vídeo automaticamente, `<iframe>` do YouTube no card (falha no AnkiMobile com "Error 153"), e os 9 cards de ordinal, que são gerados em código e não vêm de lista nenhuma.

## Capabilities

> **Ordem de arquivamento: depois de `lacunas-e-erros-do-ines`.** As duas changes
> modificam os mesmos três requisitos — `Pendências viram tags, nunca omissão`,
> `Relatório de execução` e `Download de vídeos sob demanda` — e um delta
> `MODIFIED` substitui o requisito inteiro. Os deltas desta change já incluem o
> texto que a outra acrescenta, então arquivar esta por último preserva as duas.
> Na ordem inversa, o `forma-incorreta` e o `mesmo-sinal` seriam apagados.

### New Capabilities

- `videos-externos`: obtenção, recorte e cache de vídeos de fora do INES, declarados nas listas de estudo.

### Modified Capabilities

- `listas-de-estudo`: o formato da linha ganha o elemento `@yt`, separado antes da decisão palavra/frase para que a URL não conte como palavra significativa. Erro de escrita na linha passa a ser reportado com origem e número, sem interromper a geração.
- `geracao-baralho`: o requisito de reprodução em desktop e AnkiMobile deixa de falar só dos vídeos do INES; a conversão para WebM passa a valer para qualquer fonte. Precedência de fonte de vídeo declarada. Tag `video-externo` acrescentada.
- `dicionario-ines`: o requisito de download sob demanda passa a admitir que o vídeo de uma nota venha de fora do INES, caso em que o download do INES não é tentado.

## Impact

**Código**
- `libras_anki/youtube.py` (novo): `VideoExterno` interpreta URL e trecho; `Externos` baixa, recorta e cacheia, contabilizando clipes, downloads e falhas.
- `libras_anki/listas.py`: `_separar_video` tira o `@yt` antes de `_interpretar`; `Item` ganha `video`, `problema` e `local`.
- `libras_anki/midia.py`: `caminho_ffmpeg()` extraído para uso comum; `ARGS_H264` novo; `ARGS_VP9` ganha `-pix_fmt yuv420p`, porque VP9 4:4:4 é profile 1 e nem todo webview decodifica profile diferente de 0.
- `libras_anki/gerador.py`: `_par_externo`; prioridade do link em `_nota_de_sinal`, `_nota_ausente` e `_nota_frase`; `Relatorio` ganha `externos` e `problemas`.
- `libras_anki/config.py`: `CACHE_EXTERNOS`.
- `requirements.txt`: `yt-dlp`, sem versão fixa — o YouTube muda o player e o yt-dlp corre atrás.

**Conteúdo**
- `README.md`: seção "Vídeos de fora do INES", a tag `video-externo` na tabela, `youtube.py` na estrutura, e a nota sobre uso de terceiros.
- 6 arquivos em `listas/` com os 10 links e os comentários atualizados.

**Baralho existente**
- Nenhum modelo de nota muda, então a reimportação atualiza no lugar.
- Os GUIDs não dependem da origem do vídeo, então as 10 palavras que ganharam clipe são as mesmas notas de antes, com histórico preservado. `falta-video` cai de 20 para 9 notas.

**Rede e disco**
- Um download por URL distinta, cacheado em `.cache/externos/`. Clipes em `.cache/videos/yt-<hash>.{mp4,webm}`, entre 20 e 90 KB cada — maiores que os 23–52 KB do INES, porque a fonte é 720p e não 240x176.

**Sem impacto**
- Formato do `.apkg`, modelos de nota, GUIDs, e o caminho dos vídeos do INES quando não há `@yt` na linha.
