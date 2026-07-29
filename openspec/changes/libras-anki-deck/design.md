## Context

Todo o desenho abaixo vem de investigação direta do `dicionario.ines.gov.br`, não de suposição. Os fatos apurados:

| Fato | Valor |
|---|---|
| Dataset completo | `https://dicionario.ines.gov.br/public/site/js/palavras.js` — 2.283.771 bytes |
| Formato | `var palavras = [ {...} ];` — array JSON puro |
| Verbetes | 5.826 (2 com `status: 0` e campos vazios) |
| Campos | `ident, id, letra, palavra, descricao, libras, exemplo, assunto, mao, video, image, classe, origem, status` |
| Vídeos | `https://dicionario.ines.gov.br/public/media/palavras/videos/<video>` — MP4, 23–52 KB |
| Imagens | `public/media/palavras/images/<image>` — **404, pasta morta**. Só o vídeo existe. |
| Tabelas auxiliares | `assuntos.js` (21), `classes.js` (19), `mao.js`, `origem.js` |

O site é estático (jQuery 1.4.2); as rotas `/letra/A`, `/alfabeto` retornam 404 — toda a navegação é client-side sobre o `palavras.js`. Não existe API.

O currículo alvo (aulas do usuário) contém: números 1–10 com distinção ordinal/cardinal/quantidade, cumprimentos, dias da semana e 14 frases completas. Cobertura lexical medida das 14 frases: **43/49 palavras (88%)** com lematização simples.

## Goals / Non-Goals

**Goals:**

- Gerar `.apkg` importável em Anki desktop e AnkiMobile, com mídia embutida.
- Treinar as duas direções (reconhecer sinal / produzir sinal) mais a estrutura gramatical.
- Permitir regerar o baralho a cada aula sem duplicar cards nem perder histórico de revisão.
- Nunca ensinar um sinal errado em silêncio: ambiguidade e falha de dado viram aviso visível.

**Non-Goals:**

- Fonte de dados secundária (avaliada e descartada — ver Decisão 7).
- Gravação, edição ou geração de vídeo.
- Sincronização com AnkiWeb, interface gráfica, empacotamento para distribuição.
- Cobrir os 5.826 verbetes — o baralho cresce conforme as aulas.

## Decisions

### 1. Consumir o `palavras.js` inteiro, não raspar página a página

O dataset é um arquivo só. Baixar uma vez, cachear em disco, e daí em diante toda busca é local e instantânea. Só os MP4 das palavras pedidas são baixados.

*Alternativa descartada:* scraping por verbete. Não existe rota por verbete — a informação simplesmente não está no HTML.

*Parsing:* extrair o trecho entre o primeiro `[` e o último `]` e passar por `json.loads`. É JSON válido; não é necessário interpretar JavaScript.

### 2. GUID = `ident` + nome do vídeo

Requisito central: regerar o baralho toda semana e reimportar sem duplicar nem perder histórico. O Anki decide isso pelo GUID da nota.

```
ident  → 3 valores duplicados (CHINELO, DOIS2, linha vazia)   PORÉM estável
id     → 0 duplicados                                          PORÉM posicional
```

`id` segue a ordem alfabética (1, 2, 3…). Se o INES publicar uma palavra nova em "A", todos os `id` deslocam e o baralho inteiro duplica na próxima importação. `ident` parece identificador interno estável (valores esparsos: 7049, 5402, 6959).

Decisão: `guid = sha1(f"ines:{ident}:{video}")`. Estável contra atualizações do dicionário e desempata as 3 colisões — `(ident, video)` dá 5.825 pares únicos em 5.826 linhas (a única colisão restante são as duas linhas vazias, descartadas por `status: 0`).

### 3. Uma nota, três templates de card — não três notas

```
              NOTA (1 sinal)
        ┌───────────┼───────────┐
        ▼           ▼           ▼
    Recepção    Produção    Gramática
    vídeo→PT    PT→vídeo    PT ↔ glosa
```

O Anki gera os três cards a partir de uma nota. Vantagens sobre três notas separadas: adicionar palavra = uma entrada; corrigir a descrição corrige os três; o *bury siblings* impede que os três irmãos caiam no mesmo dia (o que seria trapaça); e a reimportação atualiza tudo de uma vez.

O card de gramática só é gerado quando a nota tem `exemplo` **e** `libras` preenchidos (template condicional do Anki), o que evita cards vazios.

### 4. Variante vs. homônimo por `descricao` + `classe`

1.446 verbetes têm sufixo numérico, formando 604 grupos. Medição:

```
 96 grupos (16%) → descricao E classe idênticas   → VARIANTE   → um card, vários vídeos
481 grupos (80%) → descricoes todas diferentes    → HOMÔNIMO   → cards separados
 27 grupos ( 4%) → misto                          → separados + aviso
```

Evidência:

```
ALMOÇO1  "A primeira das duas principais refeições do dia."  mão 121  ┐ variante
ALMOÇO2  "A primeira das duas principais refeições do dia."  mão 121  ┘

ABANDONAR1  "Desprezar, largar, deixar de cuidar."             mão 101  ┐ homônimo
ABANDONAR2  "Deixar pessoa ou objeto, sem intenção de retomá-lo." mão 132 ┘

OBRIGADO1  interj.  "Grato; agradecido."                 ┐ homônimo
OBRIGADO2  adj.     "Quem tem o dever; imposição legal." ┘
```

Juntar `OBRIGADO1` e `OBRIGADO2` ensinaria que existem dois sinais intercambiáveis para agradecer — falso e prejudicial. A regra é automática e não exige curadoria manual.

*Caso especial valioso:* em `UM1`/`UM2` a regra classifica como homônimo (descrições diferentes), e está certa — mas a diferença real é **função gramatical**, não sentido:

```
UM1  mão 12  "O primeiro de todos os números inteiros."                    → cardinal
UM2  mão 82  "Algarismo representativo para QUANTIDADE dos números..."     → quantidade
```

Ou seja: o INES *codifica* a distinção cardinal/quantidade que a aula ensina, só que em prosa livre em vez de campo estruturado. Os cards de número 1–10 exploram isso (ver Decisão 6).

### 5. Anomalias da base viram tag, não exceção

```
DOIS1   ident 2483   mão 133   dois1Sm_Prog001.mp4
DOIS2   ident 2484   mão 100   doar2Sm_Prog001.mp4   ← vídeo de DOAR2 (46 KB)
DOIS2   ident 2484   mão 100   dois2Sm_Prog001.mp4   ← correto (29 KB)
```

Existe `DOAR2` com `ident 7362` usando esse mesmo `doar2Sm_Prog001.mp4`. São arquivos distintos, então não é só nome repetido — é dado corrompido, e atinge exatamente um dos dez números pedidos.

Ao todo **16 vídeos são compartilhados por dois verbetes**. Nem todos são erro:

```
legítimo:   CHEIRAR/CHEIRO1 · COMUNGAR/COMUNHÃO · DIVIDIR3/DIVISÃO
            (em LIBRAS o mesmo sinal serve para verbo e substantivo relacionado)
erro:       CHILENO/CHINELO · DEFICIENTE1/DIREITO1 · DOAR2/DOIS2
```

Distinguir automaticamente exige entender relação semântica — fora de escopo. Decisão: quando um vídeo é usado por mais de um verbete, marcar ambas as notas com `video-suspeito` e registrar no relatório. O usuário confere no Anki em vez de decorar errado. `DOIS2` recebe tratamento explícito: descartar a linha cujo vídeo não corresponde ao prefixo da palavra.

### 6. Números 1–10 como cards de contraste

O bloco de números é morfológico: a mesma configuração de mão muda de sentido pelo movimento (ordinal 1–9 = trêmulo; cardinal = parado; quantidade 1–4 = forma própria). Um card "3 → vídeo" ensina uma das três formas e esconde as outras.

Onde o INES tem os dois verbetes (`UM1`/`UM2`, `TRÊS1`/`TRÊS2`), gerar um card que apresenta os dois vídeos lado a lado e pergunta qual é qual. O trêmulo do ordinal não existe na base — esses cards nascem com `falta-video`.

Também não existem: **13, 18, 19, 90, e todas as centenas de 500 a 900** (nem `CENTO`). Por isso o escopo é 1–10, onde a cobertura é completa.

### 7. Fonte única: INES

Spread the Sign foi testado e cobre 7 lacunas (`terça-feira`, `atrasado`, `libras`, `mãe`, `ela`, `ótimo`, `fim de semana`), com MP4 de pessoa real acessível por URL direta. Descartado por três motivos:

1. A página institucional proíbe explicitamente: *"It is prohibited to download or use our videos or data without permission."* Sem licença pública, sem API.
2. **Não resolve o problema que motivou a busca.** `BOM DIA`, `BOA TARDE`, `BOA NOITE`, `DE NADA` e `ATÉ AMANHÃ` faltam nos **dois** dicionários. Dois acervos independentes omitindo os mesmos itens é evidência de que são construções compostas (BOM + DIA em sequência), não itens de léxico.
3. Dados mais pobres — só palavra → vídeo, sem `descricao`, `exemplo` ou glosa — e exigiria raspar página a página.

Manuário (INES) é vocabulário acadêmico, sem dados estruturados. VLibras/WikiLibras tem 17 mil sinais e licença aberta, mas é avatar 3D e não vídeo humano; fica anotado como último recurso futuro.

O modelo de nota guarda o vídeo sem registrar procedência, então acrescentar uma fonte depois não quebra nada.

### 8. Vídeo no card: `<video>` com dois `<source>`, WebM antes de MP4

Sinal de LIBRAS dura ~1 segundo; o **loop** é o que permite observar. `playsinline` é obrigatório no AnkiMobile — sem ele o iOS abre o vídeo em tela cheia a cada card, inviabilizando a revisão.

**Corrigido após teste.** A primeira versão desta decisão era `<video src="x.mp4">` com o MP4 do INES direto. Falhou: o player renderiza vazio no Anki desktop. O arquivo estava íntegro — H.264 (avc1), 240×176, 3,08 s, 37 quadros, e um quadro extraído mostra a sinalizadora corretamente. O que falta é o **decodificador**: o webview do Anki desktop (QtWebEngine) não traz H.264, por ser codec proprietário. É justamente por isso que o Anki toca mídia via `[sound:]`/mpv em vez de HTML.

O suporte é assimétrico entre as plataformas usadas:

```
Anki desktop (QtWebEngine)  →  WebM/VP9 ✓   H.264 ✗
AnkiMobile   (WebKit iOS)   →  H.264 ✓      WebM só em iOS recente
```

Escolher um formato só quebra em algum lado. Solução: os dois no mesmo elemento, deixando cada plataforma pegar o primeiro `<source>` que sabe decodificar.

```html
<video autoplay loop muted playsinline>
  <source src="x.webm" type="video/webm">   <!-- desktop -->
  <source src="x.mp4"  type="video/mp4">    <!-- iOS -->
</video>
```

**Resultado do teste das quatro variantes:**

| | `<video>`+MP4 | `<video>`+WebM | `[sound:]` | duplo `<source>` |
|---|---|---|---|---|
| Anki desktop | vazio | **toca** | toca | **toca** |
| AnkiMobile | toca | toca | toca | **toca** |

O iOS acabou aceitando os dois codecs, então na prática só o desktop restringe. O duplo `<source>` é mantido mesmo assim: custa pouco e protege contra variação de versão do QtWebEngine, que é justamente onde o problema apareceu.

A conversão usa o ffmpeg empacotado no `imageio-ffmpeg` (sem instalação separada no sistema): `libvpx-vp9 -crf 32 -an`, ~0,3 s por vídeo. Medido em cinco sinais, o WebM sai **33–45% menor** que o MP4 original, então guardar os dois custa ~49 KB por sinal — cerca de 15 MB para 300 sinais.

*Alternativa descartada:* `[sound:x.mp4]`. Funciona em toda plataforma porque passa pelo mpv, fora do webview — mas não faz loop e no desktop abre em janela separada. Fica como plano B se o duplo `<source>` falhar em alguma versão do AnkiMobile.

A validação vem antes de qualquer outra tarefa, e provou o seu valor: o problema apareceu com 6 cards em vez de 300.

### 9. Busca tolerante e o que fazer quando falha

As listas são escritas em português corrente; a base é em caixa alta, acentuada e no infinitivo. A resolução tenta, em ordem: exato → sem acento e sem caixa → sem sufixo numérico → lematização simples (tabela de flexões comuns: `cheguei`→`CHEGAR`, `vou`/`vamos`→`IR`, `está`/`estou`/`estão`→`ESTAR`, `minha`→`MEU`, `horas`→`HORA`).

Sem lematização a cobertura das 14 frases é 57%; com ela, 88%.

Quando nada resolve, **o card é gerado assim mesmo**, com tag `falta-video` e o verso listando o vocabulário que foi reconhecido. Pular em silêncio esconderia a lacuna; falhar com erro impediria de estudar o resto. As 6 ausências reais medidas:

| Palavra | Situação |
|---|---|
| `Ela` | só existe `ELE` — **não é falha**: em LIBRAS o pronome de 3ª pessoa é apontar, sem gênero |
| `mãe` | existe `MAMÃE1`/`MAMÃE2` — resolver por tabela de sinônimos |
| `Terça-feira` | buraco real (há segunda, quarta, quinta, sexta, sábado, domingo) |
| `atrasado` | buraco real |
| `Libras` | só `LIBRA` (peso/signo) |
| `Lulu` | nome próprio → datilologia |

### 10. Listas de estudo em arquivos versionados

Os 21 assuntos do INES são categorias concretas (ALIMENTO, ANIMAL, CORPO, FAMÍLIA…) e **64% dos verbetes caem em `NENHUM`**. Não existe assunto "saudações", e filtrar possessivos por classe gramatical falha — `PRON. POSS.` tem só `NOSSO` e `SEU`, enquanto `MEU1`/`MEU2` estão como `PRONOME`.

Portanto: agrupamento temático vem de listas mantidas pelo usuário (`listas/saudacoes.txt`, `listas/numeros.txt`, `listas/frases-aula-03.txt`), não de consulta ao campo `assunto`. Como efeito colateral desejável, as listas viram um registro versionado do próprio progresso nas aulas.

## Risks / Trade-offs

- **O `palavras.js` muda de formato ou some** → o cache local mantém o baralho funcionando; o parser valida a estrutura e falha com mensagem clara em vez de gerar dados corrompidos.
- **Vídeo errado passa despercebido** → os 16 compartilhados são marcados com `video-suspeito`; `DOIS2` é tratado explicitamente. Casos não detectados dependem de conferência humana — é limitação aceita e documentada.
- **Regra variante/homônimo erra num caso de borda** → os 27 grupos "mistos" são separados e sinalizados, favorecendo cards a mais em vez de um sinal errado.
- **`<video>` se comporta mal em alguma versão do AnkiMobile** → validar com poucos cards antes de gerar em escala; `[sound:]` permanece como plano B, custando só o loop.
- **Cards de gramática cedo demais** → o usuário está começando; frase solta sem vocabulário base vira decoreba. Os cards são gerados, mas a recomendação é suspendê-los no Anki até o vocabulário firmar. Um clique, zero retrabalho.
- **Uso dos vídeos do INES** → material do governo brasileiro, uso pessoal de estudo, sem redistribuição. O `.apkg` gerado não é para publicação.

## Migration Plan

Não se aplica — projeto novo, sem código ou dados existentes. A "migração" recorrente é a reimportação semanal, coberta pelo GUID estável (Decisão 2).

## Open Questions

- O trêmulo dos ordinais e as saudações compostas precisam de vídeo gravado em aula. Formato e origem desse material ainda não estão definidos — até lá esses cards ficam com `falta-video`.
- As glosas em LIBRAS das 14 frases da apostila não estão anotadas. Os cards nascem com `falta-glosa`; falta confirmar com a professora.
- A tabela de lematização é manual e cobre o vocabulário atual. Se as listas crescerem muito, pode valer uma biblioteca de stemming em português — mas só quando a tabela manual doer.
