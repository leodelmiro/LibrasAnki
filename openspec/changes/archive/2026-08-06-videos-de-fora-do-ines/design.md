## Context

O INES tem 5.824 verbetes e ainda assim faltam palavras de uso diário: `TERÇA-FEIRA` (com segunda, quarta, quinta, sexta, sábado e domingo presentes), `TELEFONE`, `TIA`, `PAMONHA`. Para essas, o card existia só para dizer que não tinha nada.

```
antes                             depois
─────                             ──────
TERÇA-FEIRA                       TERÇA-FEIRA
  ⚠ Sem vídeo disponível            [clipe do YouTube, 4s]
    — grave na aula.                ⚠ Sem verbete no INES.
                                      Vídeo de fonte externa:
  tag: falta-video                    youtu.be/AAA
                                    tag: video-externo
```

## Goals / Non-Goals

**Goals:**

- Resolver hoje as lacunas que têm vídeo em algum lugar, em vez de esperar gravação.
- Deixar o estudante escolher o vídeo quando ele discorda do INES, sem sair do fluxo das listas.
- Manter o baralho autocontido e offline, como já é.

**Non-Goals:**

- Buscar vídeo automaticamente por palavra. Achar o sinal certo num canal exige assistir; automatizar isso poria vídeo errado no card com cara de certo.
- Cobrir os 9 ordinais. Eles não vêm de lista — `numeros.ordinais_pendentes()` os sintetiza — então o `@yt` não os alcança por construção. Fica para um change próprio.
- Redistribuir os clipes. Mesma regra do resto do baralho: estudo pessoal.

## Decisions

### 1. Baixar e embutir, não `<iframe>`

O caminho mais curto seria um `<iframe>` do YouTube no card, com `?start=&end=`. Descartado:

| | `<iframe>` | baixar e embutir |
|---|---|---|
| AnkiMobile (iOS) | **falha**, "Error 153 — Video player configuration error" | funciona |
| Anki desktop | funciona | funciona |
| offline | não | sim |
| vídeo sai do ar | card quebra | cache preserva |
| `autoplay loop muted` dos outros cards | comportamento diferente | idêntico |

O AnkiMobile decide sozinho: o estudo acontece no iPhone, e o `<iframe>` não funciona lá.

### 2. Recorte com reencode, não `-c copy`

Cortar sem reencodar é mais rápido e não perde qualidade, mas só corta em keyframe. O intervalo de keyframe do YouTube fica entre 2 e 5 segundos — num sinal de 3 segundos, o erro é do tamanho do clipe. Reencode é obrigatório, e portanto um encoder H.264 também.

Verificado antes de construir: o ffmpeg empacotado pelo `imageio-ffmpeg` traz `libx264` e `libvpx-vp9`. Sem `libx264` o MP4 seria impossível e o iPhone ficaria sem vídeo nos cards de fora — metade da utilidade.

### 3. Cache em duas camadas

```
listas/aula-07.txt
   libras     @yt https://youtu.be/AAA 1:23-1:27
   intérprete @yt https://youtu.be/AAA 2:05-2:09
                        │
                        ▼  yt-dlp, uma vez por URL
        .cache/externos/fonte-<hash-da-url>.webm
                        │
       ┌────────────────┴────────────────┐
       ▼ ffmpeg -ss 83 -t 4              ▼ ffmpeg -ss 125 -t 4
  .cache/videos/yt-<hash>.webm   (VP9,   desktop)
  .cache/videos/yt-<hash>.mp4    (H.264, iPhone)
```

O hash do clipe deriva de URL + início + fim, então duas palavras que apontam para o mesmo trecho compartilham o arquivo. É o caso de `vosso` e `vossa`, que levam o mesmo link porque o vídeo mostra as duas formas: um download, um clipe, dois cards.

### 4. O link substitui o vídeo do INES, não empilha

Quando a palavra já tem vídeo no INES, duas saídas eram possíveis: mostrar os dois rotulados, ou trocar.

Empilhar é mais fiel ao "nada some", mas quebra o card de recepção: a frente passa a mostrar dois vídeos, e se forem variantes diferentes do sinal, a pergunta "que palavra é esta?" fica ambígua. E se você foi atrás de outro vídeo, foi porque quer decorar aquele — mostrar o do INES junto anula a escolha.

Substituir, com o registro em outro canal: a observação diz que o vídeo é de fora e que o INES também tem um, e a tag `video-externo` permite achar todos depois. Nada é escondido; o card é que ensina um sinal só.

### 5. Um link, vários verbetes: vai para o primeiro

`pessoa` resolve para PESSOA1 ("ser humano") e PESSOA2 ("indivíduo, sujeito") — homônimos, dois cards. Um link não diz qual dos dois ilustra, e aplicá-lo aos dois poria o mesmo vídeo em cards de significados diferentes, que é exatamente o erro que a separação de homônimos existe para evitar.

Vai para o primeiro, e o relatório avisa qual recebeu. A contagem é de **sinais**, não de verbetes: `vô` resolve para VOVÓ-VOVÔ1 e VOVÓ-VOVÔ2, que são variantes do mesmo sinal e viram um card só — aí não há escolha nenhuma a avisar.

### 6. O link pertence ao sinal, e por isso precisa de um pré-passo

A primeira versão tratava o `@yt` como propriedade da linha: o clipe ia para a nota daquela linha e acabava ali. O verso das frases continuava montando o vocabulário só com vídeo do INES.

Isso deixava dois buracos. O visível: `DORMIR` tem verbete, mas o campo `video` aponta `dormir2Sm_Prog001.mp4`, que dá 404 — enquanto `dormirSm_Prog001.mp4` existe no servidor. Erro de cadastro da base, não lacuna. O card da palavra estava resolvido pelo clipe; as duas frases com o verbo continuavam no aviso "sem sinal no INES", com o vídeo já baixado em cache. O invisível: quem declara um clipe porque prefere aquele vídeo via o do INES reaparecer no verso da frase, decorando duas versões do mesmo sinal.

O link passa a valer para o sinal. Isso obriga a um pré-passo: as listas são lidas em ordem alfabética, `frases-*.txt` vem antes de `verbos.txt` e `vocabulario-diverso.txt`, então na hora de montar o verso o clipe ainda não seria conhecido. `_indexar_externos` percorre todos os itens antes de qualquer nota sair.

O índice tem duas chaves porque há dois casos. Palavra que resolve é indexada pelo sinal — mesma regra do card, o link vale para o primeiro verbete resolvido (decisão 5). Palavra que não resolve, como `libras` ou `pamonha`, é indexada pelo texto normalizado: não há verbete a que se prender, e é justamente esse caso que cobre as sete frases que falam de Libras.

### 7. "Clipe longo" medido no arquivo, não no `@yt`

Um `@yt` sem trecho pode ser um vídeo de dez minutos entrando inteiro por esquecimento, ou um clipe de quatro segundos que já é só o sinal. A primeira versão avisava sempre que faltava o trecho, e disparou nos 7 links reais — todos entre 3 e 16 segundos. Falso positivo em 100% dos casos é ruído, e ruído treina a ignorar o relatório.

A duração passou a ser lida do clipe pronto, com o ffmpeg. Só avisa acima de 30 segundos, que é bem mais que qualquer sinal.

### 8. Dois player clients do yt-dlp

Dois dos vídeos usados respondiam "This video is not available" ao client padrão e abriam normalmente no navegador. Testados os seis clients disponíveis: só o `android` os entrega; `ios`, `mweb`, `web_embedded` e `web_safari` dizem "Requested format is not available" e `tv` diz "DRM protected".

`CLIENTES = ["default", "android"]` faz o yt-dlp tentar em ordem em vez de desistir no primeiro. Não é contornar restrição de acesso: são vídeos públicos, é incompatibilidade de client.

### 9. Erro de escrita na linha não derruba a geração

Uma URL torta poderia abortar a leitura da lista com a posição do erro. Mas o projeto já decidiu o contrário para o resto — nada é descartado em silêncio, e nada aborta o baralho inteiro por causa de um item. Uma linha com `@yt` malformado vira card normal, sem o vídeo, e o problema aparece no fim como `familia.txt:18 — não parece uma URL: 'url-torta'`.

## Risks / Trade-offs

- **yt-dlp quebra quando o YouTube muda o player.** Por isso a dependência não tem versão fixa e o README manda atualizar quando downloads começarem a falhar sem motivo. Não há como blindar contra isso.
- **Vídeo removido do YouTube.** O cache preserva o que já foi baixado, mas `.cache/` não é versionado: quem clonar o repo depois de o vídeo sair do ar não regenera aquele clipe. Aceito — o alvo é uma máquina só.
- **Clipes maiores que os do INES.** 20–90 KB contra 23–52 KB, porque a fonte é 720p contra 240x176. A escala é limitada a 480 px de largura para segurar isso; um baralho de centenas de sinais segue na casa dos poucos megabytes.
- **Termos de serviço do YouTube.** Baixar vídeo os contraria, mesmo para uso próprio. Está escrito no README, com a decisão deixada para quem usa.
