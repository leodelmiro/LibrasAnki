## Context

A aula pediu 30 palavras de família, os 12 meses e 11 frases. Auditando contra o dicionário em cache, o quadro é este:

```
já no baralho    família, pai, mãe, irmão, irmã, vô/vó, tia        6
tem verbete      mão, filho, esposa, solteiro, namorar, casar,    19
  e vídeo        sobrinho, cunhado, bisavô/bisavó, padrasto,
                 madrasta, adotivo, genro, nora, sogro, mês
                 + os 12 meses do ano
sem verbete      filha, sobrinha, cunhada, sogra, prima            5
  (só o          — o INES cataloga só o masculino, como já
  masculino)       acontecia com IRMÃ
sem verbete      tio                                               1
  nenhum         — o único parecido é TIARA
verbo ausente    noivar — a base tem NOIVO1 e NOIVO2               1
```

Das 11 frases, **nenhuma palavra é lacuna real** do dicionário. `bastante` não tem verbete, mas é `MUITO` — decidido na aula. Todo o resto falha por flexão (`conheci`, `nasceu`, `compras`, `trabalha`, `vão`, `faz`, `ajuda`, `ensino`, `são`, `outra`) ou por gênero/número que a tabela ainda não cobre (`amigas`, `cunhadas`, `duas`, `avós`).

Duas descobertas mudaram o desenho:

**1. Os avós são inalcançáveis pela escrita.** O sinal está no baralho — `vô` e `vó` resolvem para `VOVÓ-VOVÔ`, servido por `@yt`. Mas `avô` não resolve para nada, e existe ainda um segundo par de verbetes, `AVÔ/AVÓ1` e `AVÔ/AVÓ2`, que a normalização jamais alcança: ela tira acento e caixa, não a barra do meio do nome.

**2. O INES declara nome de arquivo errado, e o arquivo certo está no servidor.** O projeto já tinha topado com isso em `DORMIR` — a base aponta `dormir2Sm_Prog001.mp4`, que dá 404, enquanto `dormirSm_Prog001.mp4` responde. Foi resolvido com `@yt`, caso a caso. Medindo agora, o padrão é sistemático:

```
verbete       declara                404   arquivo que responde
───────       ───────                ───   ────────────────────
DORMIR        dormir2Sm              404   dormirSm
FOLGA1        folgaSm                404   folga1Sm
PESSOA1       pessoaSm               404   pessoa1Sm
NORA          nora2Sm                404   noraSm
JUNHO         junho1Sm               404   junhoSm
COMPRAR1      comprarSm              404   comprar1Sm
AGOSTO1       agostoSm               404   agosto1Sm

AVÔ/AVÓ1-2    avo.avoSm, avo.avo2Sm  404   nenhum
VOVÓ-VOVÔ1-2  vovo1Sm, vovo2Sm       404   nenhum
FEMININO      femininoSm             404   nenhum
```

É sempre o **sufixo numérico** que está trocado. `JUNHO` e `NORA` são itens pedidos nesta aula, e cair em `falta-video` com o arquivo disponível no servidor seria mentira do card.

## Goals / Non-Goals

**Goals:**

- Entregar as 30 palavras, os 13 cards de calendário e as 11 frases com o material que o INES de fato tem.
- Recuperar o vídeo quando o nome declarado estiver errado, sem inventar fonte externa para o que a base já serve.
- Manter cada decisão de gênero declarada em tabela, com o motivo em comentário, revisável depois da aula sem mexer em código.

**Non-Goals:**

- Varrer os 5.826 verbetes atrás de todos os nomes errados. Custaria uma requisição por vídeo; os casos entram quando as listas os pedirem, como `MESMO_SINAL` já faz.
- Decidir se os femininos de parentesco marcam gênero em LIBRAS. Isso é pergunta de aula, não de dicionário — o desenho só garante que a resposta caiba numa linha de tabela.
- Trocar os `@yt` existentes de `DORMIR`, `FOLGA` e `PESSOA` pelo vídeo do INES recuperado. Vídeo de fora tem precedência declarada, e mudar o vídeo de um card que já funciona não é o que esta mudança pede.

## Decisions

### 1. Os cinco femininos entram em `SINONIMOS`, não como card próprio

Decisão do usuário, e o precedente é `IRMÃ` → `IRMÃO`, que está no baralho desde o começo pelo mesmo motivo: o INES cataloga só o masculino e descreve o verbete sem marcar gênero.

Em dois dos cinco o próprio dicionário sustenta a leitura:

```
PRIMO      "O filho ou a filha de sua tia."
CUNHADO    "O irmão (ou irmã) do seu marido ou da sua mulher."
```

`FILHO`, `SOBRINHO` e `SOGRO` não trazem a ressalva, e é aí que mora o risco (abaixo).

Alternativa considerada: card próprio com `falta-video`, deixando a lacuna visível. Rejeitada porque produziria cinco cards vazios num tema em que o sinal masculino já está ali — e porque, se a resposta da aula for "é o mesmo sinal", os cinco cards vazios teriam sido trabalho jogado fora.

### 2. `avô`/`avó` apontam para `VOVÓ-VOVÔ`, não para `AVÔ/AVÓ`

Os quatro verbetes dão 404 e nenhum tem variante de nome que responda, então a escolha não é entre dois vídeos — é entre um sinal que o baralho já ensina por `@yt` e dois verbetes que não entregam nada.

`AVO` → `VOVÓ-VOVÔ` faz `avô`, `avó` e `avós` caírem no card que já existe, com o clipe que já funciona. Nenhuma linha nova nas listas: `vô` e `vó` continuam sendo as entradas, e o sinônimo serve as frases.

Alternativa considerada: `AVO` → `AVÔ/AVÓ`, que é o verbete de nome mais próximo. Daria um segundo card de avós, sem vídeo, para o mesmo sinal.

### 3. `tio` reaproveita o `@yt` de `tia`

Decisão do usuário. `TIO` não existe no INES em forma nenhuma, e a `tia` já vem de vídeo de fora — a mesma URL na linha do `tio` resolve, do jeito que `vosso`/`vossa` já compartilham um link.

O comentário da lista MUST dizer que é reaproveitamento e não confirmação, para que quem revisar depois da aula saiba o que checar.

### 4. Recuperação por sufixo, com guarda do dono declarado

Quando o download falha, tenta-se o mesmo nome com o sufixo numérico trocado (`""`, `1`, `2`, `3`), e aceita-se o primeiro que responda **e que nenhum outro verbete declare como seu**.

A guarda não é zelo excessivo, é o que separa a regra de um bug:

```
SER2 declara ser3Sm         404
  candidato serSm           404
  candidato ser1Sm          200  ← mas é o vídeo declarado por SER1
  candidato ser2Sm          200  ← livre, aceito
```

Sem a guarda, `SER2` ("expressão enfática de afirmação") mostraria o sinal de `SER1` ("figura; forma; estado"). A spec de download já proíbe emprestar vídeo entre sinais parecidos; a guarda é como essa proibição sobrevive à automação.

Verificado nos sete casos conhecidos: todo candidato bom (`dormirSm`, `folga1Sm`, `pessoa1Sm`, `noraSm`, `junhoSm`, `comprar1Sm`, `agosto1Sm`) é declarado por ninguém, e o único candidato perigoso é o de `SER2`, que a guarda recusa.

Alternativa considerada: `@yt` manual para cada caso, que foi o que se fez com `DORMIR`. Não escala — são pelo menos sete e a cada lista nova aparecem outros — e registra como "vídeo de fora" um arquivo que é do próprio INES, o que é falso na observação do card e no relatório.

Alternativa considerada: tabela `VIDEO_CORRIGIDO` mapeando verbete → nome certo, à mão. Honesta e auditável, mas cada entrada custa uma investigação manual que a regra faz sozinha em três requisições.

### 5. O plural reaplica lema e sinônimo, em vez de a tabela repetir as formas

Hoje o passo de plural só refaz a busca direta pelo singular. Se ela falhar, os passos seguintes usam de novo a forma plural, e o resultado é que `cunhada` resolve e `cunhadas` não.

Duplicar as entradas (`CUNHADA` e `CUNHADAS`, `AVO` e `AVOS`, `AMIGA` e `AMIGAS`) funcionaria e é o que exigiria menos código. Rejeitado porque a duplicação não tem fim: toda entrada futura passaria a precisar de duas linhas, e esquecer a segunda falha em silêncio, exatamente no caso — palavra dentro de frase — em que ninguém está olhando.

### 6. `MAIÔ` em `IGNORADOS`

`MAIO` e `MAIÔ` viram a mesma chave sem acento. É o caso de `CARNE`/`CARNÊ` de novo, e a tabela já existe para isso: o termo resolve normalmente, só o verbete parasita sai do índice.

### 7. Os meses em arquivo próprio

`listas/meses.txt`, e não uma seção de `vocabulario-diverso.txt`. Cada arquivo é um agrupamento temático e um registro de progresso — o calendário é um tema, e `mês` mora junto dele.

## Risks / Trade-offs

**Os femininos podem marcar gênero em LIBRAS** → Se `FILHA` for `FILHO` + `MULHER`, o card ensina metade do sinal com cara de completo, que é o defeito que o projeto mais evita. Mitigação: o comentário da lista nomeia os cinco e diz que a confirmação é de aula; desfazer é tirar a linha de `SINONIMOS` e pôr `@yt`, sem tocar em lógica. Os dois casos que o INES descreve sem gênero (`PRIMO`, `CUNHADO`) são os mais seguros; `FILHO`, `SOBRINHO` e `SOGRO` são os de conferir primeiro.

**`tio` mostrando o vídeo de `tia`** → Mesmo risco, mais agudo: aqui nem o dicionário opina, porque não há verbete. Mitigação: o comentário registra que é reaproveitamento decidido, não sinal confirmado.

**A regra de sufixo pode aceitar um arquivo órfão que não seja o sinal certo** → Um arquivo que responde e que ninguém declara pode ser sobra de cadastro antigo. Mitigação: a tag `video-renomeado` e o bloco do relatório nomeiam verbete e arquivo, então o card fica auditável em vez de silencioso — mesmo tratamento de `mesmo-sinal`.

**Custo de rede** → Até três requisições extras por vídeo que der 404. Poucos verbetes caem nisso e só na primeira geração; o cache absorve o resto.

**GUID e reimportação** → Nada muda de texto nem de modelo, então tudo é acréscimo e o histórico de revisão fica intacto. Sem nota órfã desta vez.

## Open Questions

Resolvidas pelo usuário antes da implementação:

- **`bastante` é `MUITO`.** Entra em `SINONIMOS`. `MUITO` tem três verbetes de descrições distintas, então a palavra cai no mecanismo de escolha de sentido que o verso da frase já tem — os três aparecem rotulados, e quem sinaliza escolhe. Com isso as 11 frases ficam cobertas por inteiro, sem nenhuma palavra sem sinal.
- **`noivar` é `NOIVO`.** Confirma o lema planejado. `NOIVO1` e `NOIVO2` têm descrições diferentes e viram dois cards, como qualquer homônimo do baralho.
