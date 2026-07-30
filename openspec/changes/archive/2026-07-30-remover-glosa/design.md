## Context

O baralho nasceu com glosa em todo lugar: campo na nota de palavra, campo na nota de frase, e um card de gramática em cada modelo. A prática mostrou que essa parte não era estudada — glosa é convenção de transcrição para estudo linguístico, não o que se pratica sinalizando.

O card de palavra já foi simplificado no commit `51168da`: saíram Exemplo, Glosa, Mão e Classe, e com eles o card de gramática de palavra. As specs de `libras-anki-deck` não acompanharam, então hoje elas descrevem três templates onde o código tem dois.

Falta a metade das frases. Lá a glosa ainda está inteira e amarrada em três lugares diferentes:

```
listas.py     "|" decide o TIPO da linha, antes de consultar o dicionário
                 ↓
gerador.py    ausência de glosa vira tag falta-glosa + bloco no relatório
                 ↓
modelo.py     campo Glosa + card Gramatica no MODELO_FRASE
```

O acoplamento em `listas.py` é o único ponto que não é remoção mecânica: a glosa não é só um dado ali, é um **sinal de tipo**.

## Goals / Non-Goals

**Goals:**

- Frase com um único card: português na frente, vídeos do vocabulário no verso.
- Nenhum vestígio de glosa no código, nas listas, no relatório ou no README.
- Specs alinhadas com o modelo de palavra que já está implementado.
- Corrigir as afirmações sobre lacunas para o que foi de fato verificado.

**Non-Goals:**

- Mudar o modelo de palavra (já feito) ou os cards de número/contraste.
- Trocar o `ID_MODELO_FRASE` — o GUID e o id do modelo continuam os mesmos, para que a reimportação atualize as notas em vez de duplicá-las.
- Integrar VLibras como fonte de sinais. A investigação concluiu que os sinais de lá são asset bundles Unity (`UnityFS`, 2018.3.1f1), não vídeo, e o endpoint que geraria vídeo pronto responde `401`. Fica registrado aqui para não ser reinvestigado.
- Remover frases do baralho ou fundi-las no modelo de palavra — foram consideradas e descartadas (ver Decisão 1).

## Decisions

### 1. Frase mantém modelo próprio, com um card

Três caminhos foram considerados:

| opção | resultado | por quê não |
|---|---|---|
| **manter `MODELO_FRASE` com 1 card** | frase = drill de produção | ✅ escolhida |
| eliminar `MODELO_FRASE` | frases viram só fonte de vocabulário | perde o exercício de sinalizar a frase inteira, que é o que a aula pratica |
| frase vira nota de palavra | reaproveita um modelo só | a frente pediria "faça o sinal" para algo que não é um sinal único; o verso misturaria vocabulário com semântica de palavra |

O card que sobra continua sendo um exercício real: lê a frase em português, sinaliza, e o verso mostra os sinais componentes para conferir. É produção, que é o lado difícil.

### 2. `|` deixa de ter significado, sem período de transição

A alternativa seria avisar por um ciclo ("`|` está obsoleto") antes de remover. Descartado: o projeto tem um usuário, as duas listas afetadas estão versionadas, e o texto após `|` some junto na mesma mudança. Um aviso de depreciação seria cerimônia sem beneficiário.

**Consequência a verificar, não presumir:** hoje `listas.py:55-57` usa a presença de glosa para classificar a linha como frase *antes* da consulta ao dicionário. Removido esse ramo, as linhas caem na heurística seguinte — resolve no INES vira palavra; senão, mais de uma palavra significativa vira frase. Para as 25 frases atuais o resultado deve ser idêntico, mas isso MUST ser confirmado comparando a contagem por tipo no relatório antes e depois, não deduzido.

### 3. O aviso de vídeo ausente fica no campo `Videos`

Já implementado, formalizado agora na spec. A alternativa anterior era um campo `Observacao` separado, que deixava o card de recepção com a frente vazia — e o Anki suprime o card nesse caso, escondendo justamente a lacuna que o projeto quer mostrar. Escrever o aviso dentro do campo faz o card existir e dizer o que falta.

### 4. Correção das afirmações de lacuna, sem adotar o VLibras

O que o projeto afirma hoje ("não existe em dicionário nenhum") é mais forte que a evidência. O verificado é: INES e Spread the Sign não têm; o VLibras tem `BOM_DIA`, `TERÇA_FEIRA`, `LIBRAS`, `TEU`, `TUA`, `VOSSO`, `VOSSA` e `FIM_DE_SEMANA` entre seus 23.432 sinais.

A correção é textual e conservadora: dizer o que foi checado e onde, sem concluir que o VLibras está certo. Um sinal composto pode aparecer como animação única lá por conveniência de renderização, o que não prova que seja item lexical distinto. O valor prático é saber **quais lacunas perguntar primeiro para a professora** — as que outro acervo registra como sinal único têm mais chance de ser sinal único.

## Risks / Trade-offs

**[Cards órfãos no Anki já importado]** → Remover um template não apaga os cards correspondentes que já existem na coleção; os cards de gramática de frase continuariam aparecendo nas revisões. Mitigação: a tarefa de verificação inclui buscar `card:Gramatica` no navegador do Anki e apagar manualmente. Documentar isso no README, porque vale para qualquer remoção futura de template.

**[Reclassificação silenciosa de linhas]** → Sem o ramo do `|`, alguma linha pode mudar de frase para palavra sem ninguém notar. Mitigação: comparar o relatório antes e depois; a contagem por tipo (`frase`, `simples`, `homonimo`, `ausente`) tem que bater.

**[Perder o estudo de estrutura]** → Sem card de gramática, nada no baralho trabalha explicitamente a ordem das palavras em LIBRAS, que difere do português. Trade-off aceito conscientemente: o card de frase ainda exige produzir a frase inteira, e a ordem se aprende na aula. Se voltar a fazer falta, a decisão é reversível — as listas guardam as frases, e um template novo pode ser acrescentado sem tocar nos GUIDs.

**[CSS órfão]** → `.glosa` e `.exemplo` ficam sem uso em parte dos modelos. Baixo impacto, mas a limpeza entra nas tarefas para o CSS não virar sedimento.

## Migration Plan

1. Código: `modelo.py` → `gerador.py` → `listas.py`, nessa ordem (do mais interno para o que orquestra).
2. Conteúdo: listas e README, incluindo a remoção do texto após `|` nas duas listas de frases.
3. Verificação: gerar o baralho completo e comparar o relatório com a saída atual (123 notas, 25 em SEM GLOSA).
4. No Anki: reimportar e apagar os cards de gramática órfãos.

Rollback: `git revert` da faixa de commits. Os GUIDs não mudam, então reverter e reimportar restaura os cards de gramática com o histórico de revisão intacto.

## Open Questions

- As duas listas de frases mantêm as frases em português mesmo depois de a glosa sair — nenhuma delas tem glosa preenchida hoje, então nada de conteúdo se perde nesta mudança. Se em algum momento uma glosa da professora tiver sido escrita num arquivo local não versionado, ela some. Vale conferir antes de aplicar.
