## 1. Resolução de termos (`indice.py`)

- [x] 1.1 Reaplicar lema e sinônimo sobre o singular quando o plural simples não achar pela busca direta, sem alterar a ordem dos demais passos
- [x] 1.2 Acrescentar a `SINONIMOS` os cinco femininos de parentesco (`FILHA`, `SOBRINHA`, `CUNHADA`, `SOGRA`, `PRIMA`), com o comentário registrando que `PRIMO` e `CUNHADO` são descritos pelo INES sem marcar gênero e que os outros três esperam confirmação de aula
- [x] 1.3 Acrescentar `AVO` → `VOVÓ-VOVÔ` a `SINONIMOS`, com o comentário explicando que `AVÔ/AVÓ1` e `AVÔ/AVÓ2` dão 404 e que a barra do nome não sobrevive à normalização
- [x] 1.4 Acrescentar a `SINONIMOS` o que as frases pedem: `DUAS` → `DOIS`, `AMIGA` → `AMIGO`, `EUA` → `ESTADOS UNIDOS`, `BASTANTE` → `MUITO`
- [x] 1.5 Acrescentar a `LEMAS` as flexões das frases: `CONHECI`, `NASCEU`, `COMPRAS`, `TRABALHA`, `VAO`, `FAZ`, `AJUDA`, `ENSINO`, `SAO`, `OUTRA`
- [x] 1.6 Acrescentar `NOIVAR` → `NOIVO` a `LEMAS`, com o comentário de que a base cataloga o substantivo e não o verbo
- [x] 1.7 Acrescentar `MAIÔ` a `IGNORADOS`, com o comentário da colisão com o mês
- [x] 1.8 Acrescentar `ME` a `VAZIAS`

## 2. Recuperação de vídeo com nome errado (`midia.py`, `gerador.py`)

- [x] 2.1 Montar o conjunto de arquivos declarados por verbete, para a guarda do dono
- [x] 2.2 Gerar as variantes de sufixo numérico do nome do arquivo (`""`, `1`, `2`, `3`), preservando o restante do nome
- [x] 2.3 Tentar as variantes só depois de o download declarado falhar, e aceitar apenas candidato que nenhum outro verbete declare
- [x] 2.4 Registrar o arquivo efetivamente usado, para a observação do card e o relatório
- [x] 2.5 Acrescentar `TAG_VIDEO_RENOMEADO` e aplicá-la à nota servida por variante, sem aplicar `falta-video`
- [x] 2.6 Acrescentar o bloco `VÍDEO RENOMEADO` ao relatório, nomeando verbete, nome declarado e nome usado
- [x] 2.7 Confirmar que a recuperação roda antes de `MESMO_SINAL` e depois do vídeo externo, mantendo a precedência já especificada

## 3. Listas

- [x] 3.1 Ampliar `listas/familia.txt` com as 24 palavras novas, mantendo os comentários existentes e acrescentando o dos femininos por sinônimo
- [x] 3.2 Declarar `tio` com o mesmo `@yt` de `tia`, registrando no comentário que é reaproveitamento decidido e não sinal confirmado
- [x] 3.3 Criar `listas/meses.txt` com `mês` e os 12 meses, comentando o caso `MAIO`/`MAIÔ` e o `AGOSTO1`/`AGOSTO2` de descrição igual
- [x] 3.4 Criar `listas/frases-familia.txt` com as 11 frases, comentando que estão cobertas por inteiro e quais palavras oferecem escolha de sentido

## 4. Verificação

- [x] 4.1 Rodar a geração completa e conferir no relatório que as 24 palavras, os 13 cards de calendário e as 11 frases entraram
- [x] 4.2 Conferir que `JUNHO` e `NORA` saem por `video-renomeado`, e não por `falta-video`
- [x] 4.3 Conferir que `SER2` não é servido pelo vídeo de `SER1`
- [x] 4.4 Conferir que `maio` gera um card só, do mês, e que `avós`, `amigas` e `cunhadas` resolvem no verso das frases
- [x] 4.5 Conferir que nenhum card já existente perdeu vídeo ou mudou de texto

## 5. Documentação

- [x] 5.1 Acrescentar `video-renomeado` à tabela de tags do `README.md`
- [x] 5.2 Descrever no `README.md` a recuperação por nome de arquivo, junto de onde `mesmo-sinal` já é explicado
