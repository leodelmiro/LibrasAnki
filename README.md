# Baralho Anki de LIBRAS

Gera baralhos Anki a partir do [Dicionário da Língua Brasileira de Sinais do INES](https://dicionario.ines.gov.br/), com o vídeo do sinal embutido no card.

---

## Preparar o ambiente

Só uma vez. Requer Python 3.

```
py -m venv .venv
.venv/Scripts/python.exe -m pip install -r requirements.txt
```

> Use barra normal (`/`), não invertida. Barra normal funciona no PowerShell e em
> shells tipo bash; a invertida é caractere de escape no bash e vira
> `command not found`.

---

## Gerar o baralho

```
.venv/Scripts/python.exe -m libras_anki
```

Lê tudo que estiver em `listas/` e escreve `out/libras.apkg`.

```
-m libras_anki listas/numeros.txt -o out/numeros.apkg   só uma lista
-m libras_anki --sem-ordinais                           sem os cards de ordinal
-m libras_anki --atualizar-dicionario                   rebaixar o dicionário
-m libras_anki --manter-cache                           não faxinar o cache no fim
```

Ao final vem um relatório do que entrou e do que precisa de atenção. Nada é descartado em silêncio.

**A geração faxina o cache no fim.** Saem as fontes de vídeo externo — os vídeos inteiros de onde os clipes foram recortados, que depois do clipe pronto não têm mais uso — e os vídeos que nenhuma nota referencia, de palavra que saiu das listas ou que passou a usar `@yt`. No baralho atual são cerca de 9 MB de 27 MB. O relatório diz o que saiu, e nomeia os vídeos órfãos: se uma palavra sumiu das listas sem querer, ela aparece ali.

Regerar depois disso não rebaixa nada — os clipes continuam em cache, e só a fonte inteira é que foi embora. Ela só volta a ser necessária se você mudar o trecho de um `@yt`, e aí baixa de novo, uma vez.

> **A faxina não roda em geração de lista avulsa.** Ali "o que não tem uso" seria o cache de todas as outras listas. `-m libras_anki listas/numeros.txt` deixa o cache intacto; `--manter-cache` desliga a faxina também na geração completa.

---

## Importar no Anki

**Desktop:** Arquivo → Importar (`Ctrl+Shift+I`) → `out/libras.apkg`

**iPhone:** o caminho mais fácil é pelo AnkiWeb — importe no desktop, clique em **Sincronizar**, e no AnkiMobile toque em **Synchronize**. Alternativa: copie o `.apkg` para o OneDrive/iCloud, abra no app **Arquivos** e escolha Compartilhar → AnkiMobile.

**Pode regerar e reimportar quantas vezes quiser.** Cada nota tem GUID estável, então o Anki atualiza as existentes preservando seu histórico de revisão e só acrescenta as novas.

> **Se um template deixar de existir, os cards antigos ficam.** O Anki não apaga
> cards ao remover um template na reimportação — eles continuam aparecendo nas
> revisões, órfãos. Para limpar: no navegador (`Ctrl+Shift+B`), busque pelo
> template, por exemplo `card:Gramatica`, selecione tudo e apague as notas ou os
> cards. Aconteceu quando o card de gramática saiu do baralho.

---

## Acrescentar palavras depois de cada aula

**1.** Escreva as palavras num arquivo em `listas/`. Um arquivo por aula funciona bem e vira um registro do seu progresso:

```
listas/aula-05.txt
─────────────────
# Aula 05 — família
mãe
pai
irmão
```

Ou acrescente linhas num arquivo existente — o gerador lê **todos** os `.txt` da pasta.

**2.** Rode `.venv/Scripts/python.exe -m libras_anki`

**3.** Importe no Anki.

Não precisa se preocupar com acento, maiúscula ou flexão: `cheguei` acha `CHEGAR`, `vocês` acha `VOCÊ`, `mãe` acha `MAMÃE`.

### Formato das linhas

```
casa                            palavra
tudo bem                        palavra (o INES tem verbetes com espaço)
Meu carro é vermelho.           frase
= bom dia                       força palavra, mesmo sem verbete no INES
# comentário                    ignorado

terça-feira @yt https://youtu.be/AAA 1:23-1:27      vídeo de fora do INES
```

O tipo sai do prefixo `=` e da consulta ao dicionário: se a linha inteira resolve como verbete, é palavra; senão, com mais de uma palavra significativa, é frase.

O agrupamento **não** vem do campo `assunto` do INES: lá os 21 assuntos são categorias concretas (ALIMENTO, ANIMAL, CORPO…), 64% dos verbetes caem em "NENHUM" e não existe nada como "saudações".

---

## O que o baralho tem

**Palavras** — 2 cards por sinal:

```
┌────────────┐  ┌────────────┐
│  Recepção  │  │  Produção  │
│ vídeo → PT │  │ PT → vídeo │
└────────────┘  └────────────┘
```

Sem vídeo no INES, o aviso "Sem vídeo disponível — grave na aula" aparece no lugar do vídeo — os dois cards continuam existindo, só que sem vídeo pra mostrar.

**Frases** — 1 card, "Sinalize esta frase": o português na frente, e no verso os vídeos do vocabulário para conferir sinal por sinal.

```
┌──────────────┐
│  Sinalizar   │
│ PT → vídeos  │
└──────────────┘
```

O baralho pratica **sinais, não notação escrita** — não existe card de glosa em nenhum modelo. Palavras carregam só o essencial para reconhecer e produzir o sinal.

Nem toda palavra da frase tem sinal no INES. As que não têm ficam de fora do vocabulário do verso e entram, em vez disso, num aviso: "Sem sinal no INES: ...". Exemplo real do baralho — a frase "O nome do meu cachorro é Lulu." mostra os vídeos de NOME, MEU e CACHORRO, mas "Lulu" vai para o aviso: nome próprio se faz por datilologia, soletrando.

O aviso é o último recurso, não o primeiro. Antes dele a palavra tem duas chances: um vídeo de fora declarado em qualquer lista (abaixo) e a tabela `EXPRESSOES` de `indice.py`, para o que é um sinal só escrito em várias palavras — "por que" vira PORQUE, "mais ou menos" vira um sinal, "o que" vira QUE, tudo antes da frase ser quebrada em palavras. Sem isso os pedaços se perdem ("que" é funcional) ou enganam ("mais ou menos" daria MAIS + OU + MENOS, três sinais sem relação com aproximação).

**Quando o INES tem mais de um sinal para a palavra, o verso mostra todos.** Rotulados pela descrição do dicionário, lado a lado, para você escolher pelo sentido da frase na hora de sinalizar:

```
┌────────────────────────────────────────────────┐
│ mora    [vídeo]                                │
│ você    [vídeo]                                │
│ Quem — Forma de identificar o proprietário…    │
│ Quem — Forma de identificar o autor de uma…    │
│ Quem — Forma de identificar ou nominar alguém  │
└────────────────────────────────────────────────┘
```

Escolher sozinho seria chutar: "qual" tem três sentidos no INES e o primeiro é o de identificar um *local*, que não serve para "qual o prato mais famoso". Quem sabe qual é o certo é quem está estudando, e a informação para decidir está ali. Esses cards levam a tag `escolher-sentido`, e o relatório lista todos ao fim da geração.

**O vocabulário do verso vem na ordem de LIBRAS, não na do português.** Repare no card acima: a frase é "Quem mora com você?", e o QUEM aparece **por último**. Em LIBRAS o interrogativo vai para o fim — MORAR COM VOCÊ QUEM — e o português põe na frente, que é exatamente onde se erra. Listar o vocabulário na ordem em que se lê treinaria o erro, então QUE, QUAL, QUEM, QUANDO, ONDE, COMO, QUANTO e PORQUE são movidos para o fim, e o card diz que fez isso. A frente continua sendo o português como se escreve: quem muda de ordem é o que você pratica sinalizando.

**Números** — quando o INES traz dois verbetes para o mesmo número, vira card de contraste em vez de vocabulário isolado, porque a mesma mão muda de sentido pelo movimento.

**Compostos** — `BOA TARDE` não existe como verbete porque se sinaliza BOA + TARDE em sequência. Em vez de um card vazio esperando gravação, o verso mostra os vídeos dos componentes na ordem:

```
┌─────────────────────────────────┐
│ BOA    [vídeo]                  │
│ TARDE  [vídeo]                  │
│                                 │
│ ⚠ Composto: BOA + TARDE em      │
│   sequência. Confirme na aula:  │
│   BOA.                          │
└─────────────────────────────────┘
```

Os componentes são declarados à mão em `gerador.py`, não deduzidos de dividir a frase — "de" não tem sinal, e `BOM` tem três sentidos diferentes no INES (situação agradável, característica positiva, roupa que veste bem). Onde a escolha saiu por eliminação em vez de conhecimento confirmado, a nota leva `confirmar-sinal` e o card diz o que checar.

### Vídeos de fora do INES

O dicionário tem lacunas reais — TERÇA-FEIRA, TELEFONE, PAMONHA não existem lá. Quando você achar o sinal em vídeo num canal de LIBRAS, o `@yt` põe ele no card em vez do aviso "grave na aula":

```
terça-feira @yt https://youtu.be/AAA 1:23-1:27      início-fim
telefone    @yt https://youtu.be/BBB 0:41+3         início+duração
pamonha     @yt https://youtu.be/CCC                clipe curto, sem recorte
```

Os tempos aceitam `M:SS`, `H:MM:SS` ou segundos. Vale também em linha de frase — aí o clipe vai no topo do verso, como "a frase sinalizada", antes dos vídeos do vocabulário.

**O link tem prioridade.** Numa palavra que o INES já cobre, o vídeo de fora *substitui* o do INES no card: se você foi atrás de outro vídeo, é ele que você quer decorar. O card registra a troca na observação e leva a tag `video-externo`, então dá para achar todos depois.

**O link vale para o sinal, não para a linha.** Declarado uma vez, o clipe também aparece no verso das frases que usam aquela palavra — e vence o vídeo do INES lá também, para você não decorar duas versões do mesmo sinal. A frase leva a tag `video-externo` e diz na observação quais palavras vieram de fora. Vale também para palavra sem verbete nenhum: um `@yt` em `libras` cobre as sete frases que falam de Libras.

### Quando o INES declara o nome de arquivo errado

Parte dos verbetes aponta para um vídeo que o servidor não entrega, com o arquivo certo lá sob **outro sufixo numérico**. `JUNHO` aponta `junho1Sm_Prog001.mp4`, que dá 404, enquanto `junhoSm_Prog001.mp4` responde normalmente. Erro de cadastro da base, não lacuna da língua.

Quando o download falha, o gerador tenta o mesmo nome com o sufixo trocado e usa o primeiro que responder. O card leva `video-renomeado` e diz na observação de qual arquivo o vídeo veio.

**Um candidato só é aceito se nenhum outro verbete o declarar como seu.** Sem essa guarda a recuperação serviria o sinal do vizinho: `SER2` aponta `ser3Sm`, que dá 404, e o primeiro nome que responde é `ser1Sm` — o vídeo de `SER1`, que é outro sinal. Ele é recusado, e `SER2` fica com `ser2Sm`.

A tentativa só acontece **depois** de o nome declarado falhar, nunca antes. É o que faz a nota voltar sozinha ao vídeo dela se o INES corrigir o cadastro — e o que impede que `AGOSTO2`, cujo vídeo funciona, seja atendido pelo arquivo que a recuperação do `AGOSTO1` acabou de gravar no cache.

Quando nem isso resolve, sobra o `@yt`: os quatro verbetes de avós do INES dão 404 e nenhum tem variante que responda, então o sinal vem de fora.

Funciona com qualquer site que o [yt-dlp](https://github.com/yt-dlp/yt-dlp) suporte, não só YouTube. Cada vídeo é baixado inteiro uma vez para `.cache/externos/` e recortado dali — um vídeo de aula de dez minutos serve dezenas de sinais pagando um download só. Os clipes saem em WebM e MP4, como os do INES, e ficam limitados a 480 px de largura.

Se um download falhar (link fora do ar, rede caída), o card volta ao que era — vídeo do INES, ou o aviso de lacuna — e a falha aparece no relatório. Quando os downloads começarem a falhar sem motivo aparente, o YouTube mudou o player: `.venv/Scripts/python.exe -m pip install -U yt-dlp` costuma resolver.

> **"This video is not available" num vídeo que abre no navegador.** Acontece: alguns vídeos públicos recusam o client padrão do yt-dlp e respondem normalmente ao do Android. Por isso `youtube.py` tenta os dois em ordem (`CLIENTES`) em vez de desistir no primeiro. Dois dos vídeos usados aqui só vêm por esse caminho.

### Tags para filtrar no Anki

| Tag | O que é |
|---|---|
| `falta-video` | sem vídeo no INES — grave na aula |
| `video-externo` | o vídeo veio de um link `@yt`, não do INES |
| `video-renomeado` | o nome de arquivo declarado no INES dá 404; o vídeo veio de outro sufixo, no mesmo servidor |
| `mesmo-sinal` | o vídeo próprio dá 404; é o mesmo sinal de outro verbete, e o card usa o dele |
| `forma-incorreta` | não existe em LIBRAS; o card mostra o sinal correto no lugar |
| `composto` | sem verbete próprio; o card mostra os componentes em sequência |
| `confirmar-sinal` | a escolha do componente saiu por eliminação — confirme na aula |
| `escolher-sentido` | o INES tem mais de um sinal para uma palavra da frase; o verso mostra todos |
| `video-suspeito` | o vídeo é usado por outro verbete; confira antes de decorar |
| `grupo-misto` | classificação ambígua, separado por precaução |
| `numero` `ordinal` `frase` | categoria |

Buscar `tag:falta-video` no Anki te dá a lista do que perguntar na próxima aula.

---

## Estrutura do projeto

```
libras_anki/
├── config.py     caminhos, URLs, constantes
├── ines.py       baixa e cacheia o dicionário (5.824 verbetes)
├── indice.py     busca tolerante a acento, caixa e flexão
├── grupos.py     variante vs. homônimo, e anomalias da base
├── midia.py      download dos vídeos e conversão para WebM
├── youtube.py    vídeos de fora do INES: download, recorte e cache
├── modelo.py     modelos de nota e templates dos cards
├── listas.py     leitura das listas de estudo
├── numeros.py    regras dos números 1–10
├── gerador.py    montagem do baralho e relatório
└── cli.py        linha de comando

listas/           suas listas de estudo
out/              baralhos gerados
.cache/           dicionário e vídeos baixados, do INES e de fora (não versionar)
openspec/         proposta, design, specs e tarefas
```

O plano completo e as decisões técnicas estão em `openspec/changes/libras-anki-deck/`:

```
openspec show libras-anki-deck
openspec status --change libras-anki-deck
```

---

## Sobre os dados

Os vídeos vêm do dicionário do INES, material público do governo brasileiro, usados aqui para **estudo pessoal**. O `.apkg` gerado não é para redistribuição.

Os clipes trazidos por `@yt` são de terceiros e ficam sob a mesma regra: estudo pessoal, sem redistribuir. Baixar vídeo do YouTube contraria os termos de serviço deles, ainda que para uso próprio — vale saber, e decidir.

O dicionário tem lacunas e alguns erros — o projeto trata isso explicitamente em vez de esconder. Palavras sem material viram cards marcados em vez de sumirem em silêncio, e verbetes com dado inconsistente recebem aviso. O raciocínio por trás de cada tratamento está em `openspec/changes/libras-anki-deck/design.md`.

Dois detalhes que valem saber ao estudar:

- Os MP4 do INES são H.264, que o webview do Anki desktop não decodifica. Cada vídeo também é convertido para WebM e o card leva os dois formatos, deixando cada plataforma escolher.
- Nem toda "lacuna" é falha do dicionário. `BOM DIA` não existe como verbete porque se sinaliza BOM + DIA em sequência; `ela` não existe porque em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero — é o mesmo sinal de `ELE`.
