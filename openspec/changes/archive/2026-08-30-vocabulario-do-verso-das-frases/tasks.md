> Implementação feita antes destes artefatos, durante a conversa que originou a
> mudança. As tarefas abaixo descrevem o que foi executado e verificado; ficam
> marcadas por refletirem o estado real do código, não por terem sido planejadas
> primeiro.

## 1. Investigação

- [x] 1.1 Auditar as 38 frases palavra por palavra, separando o que cai no aviso do que some sem aviso nenhum
- [x] 1.2 Levantar os 18 grupos de homônimo usados pelas frases e comparar as descrições do INES com o sentido de cada frase
- [x] 1.3 Confirmar que `QUAL1` é "identificar um local" e que nenhuma das duas frases com `qual` pergunta local
- [x] 1.4 Confirmar que `QUE2` existe e tem como exemplo cadastrado "O que você quer beber?", e que `QUE1` é o "quê?" de não ter entendido
- [x] 1.5 Confirmar que `MAIS OU MENOS` não tem verbete, e que os três pedaços resolvem para `MAIS 1`, `OU` e `MENOS1`
- [x] 1.6 Separar os grupos que são escolha real dos que são variante de descrição igual (`MEU1`/`MEU2`, `FOLGA1`/`FOLGA2`)

## 2. Expressões de várias palavras

- [x] 2.1 Criar `EXPRESSOES` e `_MAIOR_EXPRESSAO` em `indice.py`, com o motivo de cada entrada em comentário
- [x] 2.2 Casar sequências em `palavras_da_frase` antes do filtro de `VAZIAS`, do maior tamanho para o menor
- [x] 2.3 Declarar `por que` → `porque`, `o que` → `que` e `mais ou menos`
- [x] 2.4 Mapear para termo e não para verbete, de modo que `o que` continue devolvendo `QUE1` e `QUE2`
- [x] 2.5 Atualizar o comentário de `FALSOS_AMIGOS["POR"]`, que passou a valer só para `por` isolado

## 3. Escolha de sentido no verso

- [x] 3.1 Criar `_sinais_de`, devolvendo os `Sinal` distintos de uma resolução pela identidade do objeto
- [x] 3.2 Criar `_rotulo_de_sentido`, montando o rótulo com a descrição do INES e caindo no nome do verbete quando não houver descrição
- [x] 3.3 Emitir um bloco por sentido em `_nota_frase`, mantendo o rótulo simples quando houver sinal único
- [x] 3.4 Acrescentar `TAG_ESCOLHER_SENTIDO` e a observação nomeando as palavras com opção
- [x] 3.5 Manter a precedência do vídeo de fora acima da escolha: link declarado é escolha já feita

## 4. Relatório

- [x] 4.1 Acrescentar `Relatorio.escolha_de_sentido` e o bloco "ESCOLHA NO VERSO"

## 5. Conteúdo

- [x] 5.1 Trocar "em média" por "mais ou menos" na frase do kg de carne
- [x] 5.2 Acrescentar `kg` a `NOTAS_DE_LINGUA`: abreviatura que se soletra K + G, não lacuna do dicionário
- [x] 5.3 Documentar a escolha de sentido no README, com exemplo de verso e a tag na tabela
- [x] 5.4 Documentar `EXPRESSOES` no README, na seção que explica o aviso de palavra sem sinal
- [x] 5.5 Reescrever os comentários de cobertura das três listas de frase, que listavam buracos que deixaram de existir
- [x] 5.6 Acrescentar `Por que você estuda Libras? → VOCÊ ESTUDAR LIBRAS PORQUE` à tabela de referência de `frases-perguntas.txt`

## 6. Verificação

- [x] 6.1 Conferir a quebra de `Quanto é mais ou menos um kg de carne?`, `Por que você estuda Libras?` e `Quero mais ou menos isso`
- [x] 6.2 Conferir que `mais ou menos` sozinho numa linha vira palavra e não frase, por reduzir a um item só
- [x] 6.3 Gerar o baralho e conferir os rótulos do verso de `O que você gosta de fazer?`, `Quem mora com você?` e `Como você vai trabalhar?`
- [x] 6.4 Confirmar que `MEU` e `FOLGA` não aparecem no bloco "ESCOLHA NO VERSO", por serem variante
- [x] 6.5 Confirmar 22 das 38 frases com `escolher-sentido`, e o aviso de palavra sem sinal caindo de 15 frases para 1
- [ ] 6.6 Reimportar no Anki, conferir os cards de escolha no desktop e no AnkiMobile, e apagar à mão a nota órfã de "Quanto é em média um kg de carne?" — **passo manual no app**
