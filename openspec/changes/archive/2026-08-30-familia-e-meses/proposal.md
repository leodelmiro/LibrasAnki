## Why

O baralho tem seis palavras de família — família, pai, mãe, irmão/irmã e vô/vó — e nenhum mês do ano. A aula seguinte pede o vocabulário inteiro do parentesco e o calendário, mais 11 frases que os exercitam, e quase nada disso é lacuna do INES: das 26 palavras que faltam, **19 têm verbete e vídeo**, e os 12 meses estão todos lá.

O que impede não é o dicionário, são três coisas do nosso lado. Os **femininos** de parentesco não existem na base (FILHA, SOBRINHA, CUNHADA, SOGRA, PRIMA), do mesmo jeito que IRMÃ não existia — o INES cataloga só o masculino. As **flexões** das frases novas não estão nas tabelas (`conheci`, `nasceu`, `compras`, `trabalha`, `vão`, `faz`, `ajuda`, `ensino`, `são`, `outra`). E `avô`/`avó`/`avós` **não resolvem** apesar de o sinal já estar no baralho: os verbetes se chamam `AVÔ/AVÓ1` e `AVÔ/AVÓ2`, e a barra no meio do nome não sobrevive à normalização.

Junto vem um defeito da base que o projeto já tinha visto em DORMIR e resolvido caso a caso: **o INES declara nome de arquivo de vídeo que o servidor não entrega, enquanto o arquivo certo está lá sob outro sufixo**. JUNHO e NORA — dois itens pedidos agora — caem nisso. `junho1Sm_Prog001.mp4` dá 404 e `junhoSm_Prog001.mp4` responde 200; `nora2Sm_Prog001.mp4` dá 404 e `noraSm_Prog001.mp4` responde 200.

## What Changes

**Conteúdo**

- `listas/familia.txt` cresce com mão, filho, filha, tio, primo, prima, esposa, solteiro, namorar, noivar, casar, sobrinho, sobrinha, cunhado, cunhada, bisavô, bisavó, padrasto, madrasta, adotivo, genro, nora, sogro e sogra.
- `listas/meses.txt`, novo: `mês` e os 12 meses do ano.
- `listas/frases-familia.txt`, novo: as 11 frases da aula.
- `tio` leva o mesmo `@yt` já declarado em `tia` — decisão do usuário, registrada no comentário da lista. TIO não existe no INES em forma nenhuma; o único verbete parecido é TIARA.

**Resolução**

- Os cinco femininos de parentesco entram em `SINONIMOS` apontando para o masculino, como `IRMÃ` → `IRMÃO` já faz. O INES sustenta isso em dois deles: PRIMO é descrito como "o filho **ou a filha** de sua tia" e CUNHADO como "o irmão (**ou irmã**) do seu marido ou da sua mulher".
- `AVO` entra em `SINONIMOS` apontando para `VOVÓ-VOVÔ` — o sinal que o baralho já ensina por `vô`/`vó`. Os verbetes `AVÔ/AVÓ1` e `AVÔ/AVÓ2` **não** são usados: os dois dão 404 no servidor, sem variante de nome que responda.
- O plural simples MUST voltar a tentar as tabelas de lema e sinônimo sobre a forma singular. Hoje ele só repete a busca direta, e por isso `avós`, `amigas` e `cunhadas` falham enquanto `avó`, `amiga` e `cunhada` resolveriam.
- `MAIÔ` entra em `IGNORADOS`: sem acento vira a mesma chave de `MAIO`, e o mês do calendário geraria também um card de traje de banho.
- `me` entra em `VAZIAS`, junto das demais funcionais.

**Vídeo declarado com nome errado**

- Quando o download do vídeo falhar, o sistema MUST tentar o mesmo nome com o sufixo numérico trocado, e MUST aceitar o candidato apenas se nenhum outro verbete o declarar como seu. A nota recebe a tag `video-renomeado`.
- A guarda não é detalhe: sem ela, `SER2` (que declara `ser3Sm`, 404) pegaria `ser1Sm`, que é o vídeo de `SER1` — um sinal por outro, exatamente o que a spec de download já proíbe.

**Fora de escopo:** varrer o dicionário inteiro atrás de todos os verbetes com nome de arquivo errado. A regra conserta os que as listas pedirem, quando pedirem; um levantamento completo da base é outra mudança.

## Capabilities

### Modified Capabilities

- `dicionario-ines`: a busca tolerante passa a aplicar lema e sinônimo sobre o singular quando o plural simples falha; e o download ganha a recuperação por sufixo de arquivo, com a guarda que impede pegar o vídeo de outro verbete.

O `listas-de-estudo` não muda: as listas novas são conteúdo, e o requisito de pendências já cobre a nota servida por vídeo recuperado — quem define que ela não recebe `falta-video` é o requisito de download, no mesmo lugar onde o empréstimo por `mesmo-sinal` já está definido.

## Impact

**Código**
- `libras_anki/indice.py`: `LEMAS` ganha 10 flexões; `SINONIMOS` ganha 9 entradas; `IGNORADOS` ganha `MAIÔ`; `VAZIAS` ganha `ME`; `resolver` reaplica lema e sinônimo sobre o singular.
- `libras_anki/midia.py`: variantes de sufixo no nome do arquivo, com a guarda do dono declarado.
- `libras_anki/gerador.py`: `TAG_VIDEO_RENOMEADO` e o bloco do relatório.

**Conteúdo**
- `listas/familia.txt` reescrita; `listas/meses.txt` e `listas/frases-familia.txt` novos.
- `README.md`: a tabela de tags ganha `video-renomeado`.

**Baralho existente**
- Nenhum modelo de nota muda; a reimportação atualiza no lugar e preserva o histórico.
- Nada é removido: as 26 palavras, os 13 cards de calendário e as 11 frases são todos acréscimo.
- `FOLGA1` e `PESSOA1` também têm arquivo sob outro nome e passam a ser servidos por ele. Os `@yt` declarados para eles continuam valendo — vídeo de fora tem precedência —, então nenhum card muda de vídeo sem alguém decidir isso.

**O que continua faltando**
- `bastante` é a única palavra das 11 frases sem verbete no INES. O verso do card avisa que ela não tem sinal, como já faz com "Lulu" — fica para a professora dizer se é MUITO ou outro sinal.
- Os quatro verbetes de avós do INES (`AVÔ/AVÓ1`, `AVÔ/AVÓ2`, `VOVÓ-VOVÔ1`, `VOVÓ-VOVÔ2`) dão 404 e nenhum tem variante de nome que responda. O sinal continua vindo do `@yt` já declarado em `vô`.
