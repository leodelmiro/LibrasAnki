## 1. Validar o template de vídeo antes de tudo

- [x] 1.1 Gerar um `.apkg` mínimo com 3 cards usando `<video autoplay loop muted playsinline>` e vídeos reais do INES
- [x] 1.2 Importar no Anki desktop e confirmar reprodução em laço dentro do card — **falhou com MP4**: o webview (QtWebEngine) não decodifica H.264 e o player vem vazio; o arquivo está íntegro
- [x] 1.3 Importar no AnkiMobile e confirmar que o vídeo não abre em tela cheia — as quatro variantes tocam no iOS, inclusive H.264 e WebM
- [x] 1.4 Diagnóstico de quatro variantes (`<video>`+MP4, `<video>`+WebM, `[sound:]`, duplo `<source>`) — WebM funciona no desktop; decisão 8 do design reescrita
- [x] 1.5 Confirmar o card D (duplo `<source>` WebM+MP4) no desktop **e** no AnkiMobile — funciona nos dois; formato definitivo
- [x] 1.6 Atualizar o `smoke_video_template.py` para o duplo `<source>`

## 2. Estrutura do projeto

- [x] 2.1 Criar o pacote Python e o layout de diretórios (código, cache, listas, saída)
- [x] 2.2 Declarar as dependências `genanki` e `requests`
- [x] 2.3 Definir o caminho de cache e criar os diretórios na primeira execução

## 3. Obtenção do dataset

- [x] 3.1 Baixar o `palavras.js` e extrair o array JSON entre o primeiro `[` e o último `]`
- [x] 3.2 Validar a estrutura e falhar com mensagem clara preservando o cache anterior se o formato mudou
- [x] 3.3 Gravar e reutilizar o cache local, sem rede quando o cache é válido
- [x] 3.4 Descartar verbetes com `status: 0`
- [x] 3.5 Baixar e cachear as tabelas auxiliares `classes.js`, `assuntos.js` e `mao.js`

## 4. Índice e busca

- [x] 4.1 Construir o índice normalizado (sem acento, caixa única, sem sufixo numérico)
- [x] 4.2 Implementar a cadeia de resolução: exato, normalizado, sem sufixo, lematizado
- [x] 4.3 Escrever a tabela de lematização cobrindo as flexões do currículo atual
- [x] 4.4 Escrever a tabela de sinônimos (ao menos `mãe` → `MAMÃE`)
- [x] 4.5 Reportar termos não resolvidos em vez de omiti-los
- [x] 4.6 Testar a resolução contra as 14 frases da apostila — medido 46/50 (92%), acima dos 43/49 previstos, graças ao mapeamento de dígitos e ao sinônimo `ela`→`ELE`
- [x] 4.7 Bloquear falsos amigos: `Libras` resolvia por plural para `LIBRA` (peso/signo) — guarda explícita adicionada palavras

## 5. Variantes, homônimos e anomalias

- [x] 5.1 Agrupar verbetes por raiz com sufixo numérico — inclui também a forma sem sufixo (`ANO` com `ANO1`/`ANO2`), o que corrige a contagem de variantes para 95
- [x] 5.2 Classificar cada grupo comparando `descricao` e `classe` — 4375 simples, 1251 homônimos, 95 variantes
- [x] 5.3 Marcar grupos mistos com `grupo-misto` e separá-los em notas distintas — 91 sinais
- [x] 5.4 Detectar vídeos compartilhados por mais de um verbete e aplicar `video-suspeito` — 28 sinais (14 pares)
- [x] 5.5 Descartar a linha de `DOIS2` cujo vídeo não corresponde ao prefixo da palavra — mesma regra pegou também `CHINELO`/`chilenoSm`
- [x] 5.6 Desempatar `ident` duplicado pelo nome do vídeo
- [x] 5.7 Verificar que `ALMOÇO` resulta em variante e `OBRIGADO` em homônimo — confirmado, e `UM1`/`UM2` também separam corretamente

## 6. Download de vídeos

- [x] 6.1 Baixar sob demanda apenas os vídeos das notas geradas
- [x] 6.2 Reutilizar o cache e evitar rede para vídeos já presentes
- [x] 6.3 Aplicar `falta-video` e registrar no relatório quando o download falhar
- [x] 6.4 Ignorar o campo `image` (diretório retorna 404)

## 7. Modelo de nota e templates

- [x] 7.1 Definir os campos da nota (palavra, descrição, exemplo, glosa, vídeos, mão, classe, origem) — mais `Observacao` para pendências
- [x] 7.2 Implementar o template de recepção (vídeo → palavra)
- [x] 7.3 Implementar o template de produção (palavra → vídeo)
- [x] 7.4 Implementar o template de gramática, condicional a `exemplo` e `libras` preenchidos — verificado: com ambos gera 3 cards, faltando qualquer um gera 2
- [x] 7.5 Suportar múltiplos vídeos identificados no mesmo card para notas de variante
- [x] 7.6 Calcular o GUID como hash de `ident` + nome do vídeo, sem usar o campo `id` — verificado: 5720 GUIDs únicos, idênticos após deslocar todos os `id`
- [x] 7.7 Estilo com suporte a modo noturno do Anki

## 8. Listas de estudo

- [x] 8.1 Ler arquivos de lista ignorando linhas vazias e comentários iniciados por `#`
- [x] 8.2 Distinguir linha de palavra de linha de frase — decidido pelo dicionário, não por espaço, já que o INES tem verbetes como `TUDO BEM` e `COM LICENÇA`
- [x] 8.3 Aceitar glosa informada pelo usuário junto da frase, separada por `|`
- [x] 8.4 Gerar notas de frase com `falta-glosa` e listar o vocabulário reconhecido no verso
- [x] 8.5 Indicar no verso quais palavras da frase não têm sinal disponível
- [x] 8.6 Gerar nota com `falta-video` para toda palavra não resolvida
- [x] 8.7 Prefixo `=` para forçar tratamento como palavra (saudações compostas)
- [x] 8.8 Modelo de nota próprio para frases — sem card de recepção, que não faz sentido sem vídeo único

## 9. Números de 1 a 10

- [x] 9.1 Gerar card de contraste quando o número tem dois verbetes com descrições distintas — saiu em `1` (`UM1`/`UM2`) e `3` (`TRÊS1`/`TRÊS2`)
- [x] 9.2 Gerar cards normais de recepção e produção quando o número tem verbete único — `2` cai em variante, `4`–`10` em simples
- [x] 9.3 Criar as notas de ordinal com movimento trêmulo marcadas com `falta-video` — 9 cards (1º–9º)
- [x] 9.4 Limitar o escopo a 1–10 e recusar números fora da faixa com mensagem explicativa

## 10. Conteúdo inicial

- [x] 10.1 Escrever `listas/numeros.txt` com 1 a 10
- [x] 10.2 Escrever `listas/saudacoes.txt` marcando as compostas ausentes (`BOM DIA`, `BOA TARDE`, `BOA NOITE`, `DE NADA`, `ATÉ AMANHÃ`)
- [x] 10.3 Escrever `listas/dias-da-semana.txt` registrando a ausência de `TERÇA-FEIRA`
- [x] 10.4 Escrever `listas/frases-apostila.txt` com as 14 frases da aula
- [x] 10.5 Documentar que `Ela` usa o mesmo sinal de `ELE`, por o pronome de 3ª pessoa em LIBRAS não marcar gênero — vira observação no verso do card

## 11. Geração e relatório

- [x] 11.1 Montar o `.apkg` com toda a mídia embutida
- [x] 11.2 Emitir o relatório com contagem de notas e de cada tag de pendência
- [x] 11.3 Listar no relatório os termos não resolvidos e as notas com `video-suspeito` e `grupo-misto`
- [x] 11.4 Expor a interface de linha de comando recebendo listas de entrada e caminho de saída

## 12. Verificação de ponta a ponta

- [x] 12.1 Gerar o baralho completo com as quatro listas iniciais — 69 notas, 139 cards, 3,1 MB, 126 arquivos de mídia (63 MP4 + 63 WebM)
- [ ] 12.2 Importar no Anki desktop e conferir os três tipos de card
- [x] 12.3 Regerar acrescentando palavras novas e confirmar que nada duplicou — 69 GUIDs preservados, 3 novos, 0 perdidos
- [x] 12.4 Conferir as notas marcadas com `video-suspeito` — nenhuma no conteúdo atual
- [ ] 12.5 Importar no AnkiMobile e revisar alguns cards de cada tipo
