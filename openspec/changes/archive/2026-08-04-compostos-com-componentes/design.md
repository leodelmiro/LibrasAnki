## Context

Seis itens das listas são compostos: se sinalizam em sequência e não têm verbete próprio no INES. Até agora eles caíam no mesmo caminho de qualquer palavra ausente — `_nota_ausente`, com `pares_video=[]` — e o card saía com o aviso "sem vídeo, grave na aula".

Mas os componentes existem, com vídeo. `BOA` e `TARDE` estão os dois no dicionário. O card estava vazio por construção, não por falta de material.

```
antes                          depois
─────                          ──────
BOA TARDE                      BOA TARDE
  ⚠ Sem vídeo disponível         BOA   [vídeo]
    — grave na aula.             TARDE [vídeo]
                                 ⚠ Composto: BOA + TARDE
  tag: falta-video                 em sequência.
                                 tags: composto, confirmar-sinal
```

## Goals / Non-Goals

**Goals:**

- Dar o que praticar hoje nos compostos, em vez de um card que só espera gravação.
- Manter rastreável de onde veio cada componente, inclusive quando a escolha foi palpite informado.
- Corrigir o defeito de `raiz()` que a investigação expôs.

**Non-Goals:**

- Inferir componentes automaticamente (ver Decisão 1).
- Acrescentar compostos além dos 6 mapeados. Novos entram quando aparecerem nas aulas.
- Buscar sinais fora do INES. O VLibras tem `BOM_DIA` como sinal único, mas os assets de lá são bundles Unity, não vídeo — já investigado e descartado.

## Decisions

### 1. Componentes declarados, não derivados

O caminho óbvio seria dividir `"boa tarde"` em palavras e resolver cada uma. Testado contra os 6 compostos, falha em três frentes:

| problema | onde aparece |
|---|---|
| palavra funcional sem sinal | `de` em "de nada"; `tenha` em "tenha um bom fim de semana" |
| homônimo com sentidos distintos | `BOM` tem 3 verbetes, `BOA` tem 2 |
| composto não é split literal | "tenha um bom fim de semana" não usa `um` |

A ambiguidade não é acadêmica: `BOA2` é "mulher atraente" e `BOM3` é "roupa que veste bem". `resolver()` devolve os verbetes na ordem da base, então pegar `verbetes[0]` seria escolher no escuro — exatamente o que `FALSOS_AMIGOS` existe para impedir.

Então `COMPOSTOS` nomeia os verbetes exatos, com o motivo de cada escolha em comentário. Fica na mesma família de `SINONIMOS`, `FALSOS_AMIGOS` e `NOTAS_DE_LINGUA`: tabelas curadas à mão, com o raciocínio ao lado.

Custo aceito: acrescentar um composto exige editar código, não só a lista. Com 6 itens que mudam raramente, é barato — e o erro que evita é ensinar o sinal errado.

### 2. `confirmar-sinal` distingue palpite de conhecimento

Entre os 6, dois são inequívocos (`até amanhã` = ATÉ + AMANHÃ, ambos únicos) e quatro dependem de escolher um `BOM`/`BOA`. Tratar os dois casos igual esconderia a diferença.

A tag separa: `composto` diz como o card foi montado, `confirmar-sinal` diz que parte da montagem é palpite informado pela descrição do INES. O card nomeia o que checar, então a dúvida chega até a aula em vez de virar decoreba de um sinal possivelmente errado.

Alternativa descartada: mostrar todos os candidatos rotulados. Mais fiel ao princípio de não esconder nada, mas "bom dia" viraria 7 vídeos num card só — o custo de uso não compensa quando o card já diz o que confirmar.

### 3. Composto com componente deixa de ser `falta-video`

A tag significa "precisa gravar material na aula". Depois desta mudança isso ficou falso para os compostos: há vídeo, o card funciona, nada precisa ser gravado. Mantê-la poluiria a busca `tag:falta-video`, que é como se descobre o que perguntar na próxima aula — de 25 itens, 6 seriam ruído.

O item continua em `nao_resolvidos` no relatório, porque continua verdade que ele não tem verbete próprio. As duas coisas são distintas e agora aparecem separadas.

### 4. `html_vocabulario` em vez de `html_videos`

`html_videos` rotula múltiplos vídeos como "variante 1, variante 2" — correto para um sinal com mais de uma forma registrada, errado para componentes, que são sinais diferentes em sequência. `html_vocabulario` já rotula cada vídeo com um nome, que é exatamente a semântica necessária, e já era usada pelas frases.

Por isso `criar_nota` ganhou `componentes` em vez de reaproveitar `pares_video`: a diferença não é de dado, é de significado.

### 5. `raiz()` passa a tolerar espaço

Bug encontrado ao investigar por que `dia` não resolvia. O INES escreve `DIA 1`, `BOLO 2`, `MAIS 1`, `REDE 1` — 9 verbetes com espaço antes do número, contra a maioria colada. `re.sub(r"\d+$", "", "DIA 1")` devolve `"DIA "`, que nunca casa com `"DIA"`.

Dois efeitos, ambos silenciosos:

- `dia` e `bolo` inalcançáveis na busca
- `MAIS` e `REDE`, que misturam os dois formatos, partidos em dois grupos quando são um sinal só

A correção é `\s*\d+$`. Afeta `grupos.classificar`, que agrupa por raiz — verificado que o baralho atual não muda, porque nenhuma das quatro palavras está nas listas.

## Risks / Trade-offs

**[A escolha do homônimo pode estar errada]** → `BOM1` e `BOA1` vieram de ler as descrições do INES e eliminar as implausíveis, não de saber LIBRAS. Mitigação: `confirmar-sinal` na nota, o que confirmar escrito no card, e o relatório listando a sequência de cada composto para revisão sem abrir o Anki. É palpite declarado, não palpite disfarçado.

**["tenha um bom fim de semana" é o mais frágil]** → Além do `BOM`, a própria sequência `BOM + FIM + SEMANA` é suposição. Mitigação: `confirmar` inclui explicitamente "a sequência", e a observação do card diz para confirmar na aula.

**[Tabela de componentes desatualiza em silêncio]** → Se o INES renomear um verbete, o nome declarado deixa de resolver. Mitigação: `_componentes` devolve os que faltaram e o card informa quais ficaram de fora, em vez de encolher a sequência sem avisar.

**[Correção de `raiz()` altera agrupamento]** → Muda a classificação de `MAIS` e `REDE`. Nenhuma está nas listas hoje, e a contagem do baralho é idêntica antes e depois (123 notas), mas alguém que acrescente `mais` numa lista verá um agrupamento diferente do que veria antes — que é o correto.

## Migration Plan

Sem migração de dados. Os 6 compostos mantêm o GUID (`ausente:<texto>`), então a reimportação atualiza as notas existentes: o campo de vídeo deixa de ter o aviso e passa a ter os componentes, e o histórico de revisão é preservado.

Rollback: `git revert`. Como o GUID não muda, reverter e reimportar devolve os cards ao estado anterior.

## Open Questions

- Se a professora confirmar (ou corrigir) as escolhas de `BOM`/`BOA` e a sequência do "tenha um bom fim de semana", a atualização é uma linha em `COMPOSTOS` mais remover o item de `confirmar`. Vale fazer na mesma aula em que perguntar.
- Outros compostos vão aparecer conforme o curso avança. A tabela é o lugar deles, mas se passar de uma dúzia vale reconsiderar se merece sair do código para um arquivo de dados.
