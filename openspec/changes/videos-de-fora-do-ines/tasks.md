> Implementação feita antes destes artefatos, durante a conversa que originou a
> mudança. As tarefas abaixo descrevem o que foi executado e verificado; ficam
> marcadas por refletirem o estado real do código, não por terem sido planejadas
> primeiro.

## 1. Verificação de viabilidade

- [x] 1.1 Confirmar que o `<iframe>` do YouTube não serve: falha no AnkiMobile com "Error 153", que é a plataforma de estudo
- [x] 1.2 Confirmar que o ffmpeg empacotado pelo `imageio-ffmpeg` traz `libx264` — sem ele o MP4 é impossível e o iPhone fica sem vídeo
- [x] 1.3 Confirmar que corte por `-c copy` não serve, por cair só em keyframe (intervalo de 2 a 5s no YouTube, contra sinais de ~3s)

## 2. Módulo de vídeo externo

- [x] 2.1 Criar `libras_anki/youtube.py` com `VideoExterno` (URL + trecho interpretado) e `Externos` (download, recorte, cache)
- [x] 2.2 Interpretar trechos em `M:SS`, `H:MM:SS` e segundos, nas formas `início-fim` e `início+duração`
- [x] 2.3 Levantar `ErroVideoExterno` para URL inválida, tempo inválido e fim antes do início
- [x] 2.4 Cachear a fonte por hash da URL em `.cache/externos/`, e o clipe por hash de URL + início + fim em `.cache/videos/`
- [x] 2.5 Configurar `CLIENTES = ["default", "android"]` no yt-dlp, com o motivo em comentário
- [x] 2.6 Escrever via arquivo temporário, para não deixar clipe truncado em cache se a escrita for interrompida

## 3. Conversão e formatos

- [x] 3.1 Extrair `caminho_ffmpeg()` para o nível do módulo em `midia.py`, reaproveitado por `youtube.py`
- [x] 3.2 Acrescentar `ARGS_H264` com `yuv420p` e `+faststart`, exigências do WKWebView
- [x] 3.3 Fixar `-pix_fmt yuv420p` em `ARGS_VP9`, porque VP9 4:4:4 é profile 1 e nem todo webview decodifica
- [x] 3.4 Limitar a largura a 480 px com `scale=w='min(480,iw)':h=-2`, já que a fonte é 720p contra os 240x176 do INES

## 4. Leitura das listas

- [x] 4.1 Criar `_separar_video` em `listas.py`, aplicado antes de `_interpretar` para a URL não contar como palavra
- [x] 4.2 Acrescentar `video`, `problema` e `local` a `Item`
- [x] 4.3 Documentar o novo formato no docstring do módulo

## 5. Montagem das notas

- [x] 5.1 Criar `Gerador._par_externo`, devolvendo None quando não há link ou o download falhou
- [x] 5.2 Dar precedência ao link em `_nota_de_sinal`, com observação registrando que o INES também tem vídeo
- [x] 5.3 Dar precedência ao link em `_nota_ausente`, acima dos componentes de composto
- [x] 5.4 Pôr o clipe no topo do verso da frase, rotulado "a frase sinalizada", antes do vocabulário
- [x] 5.5 Aplicar o link ao primeiro sinal quando o item resolve para vários, contando sinais e não verbetes

## 6. Relatório

- [x] 6.1 Acrescentar `Relatorio.problemas` e o bloco "PROBLEMAS NAS LISTAS", com `arquivo:linha`
- [x] 6.2 Acrescentar o bloco "VÍDEO EXTERNO FALHOU", com o motivo de cada falha
- [x] 6.3 Acrescentar o bloco "CLIPE LONGO", medindo a duração no arquivo pronto e não na ausência de trecho
- [x] 6.4 Acrescentar a linha de resumo com clipes gerados, clipes de cache e downloads

## 7. Conteúdo

- [x] 7.1 Acrescentar `yt-dlp` a `requirements.txt`, sem versão fixa, com o motivo em comentário
- [x] 7.2 Escrever a seção "Vídeos de fora do INES" no README, com sintaxe, prioridade e o caso do client do yt-dlp
- [x] 7.3 Acrescentar `video-externo` à tabela de tags e `youtube.py` à estrutura do projeto
- [x] 7.4 Registrar no README que os clipes de terceiros seguem a regra de estudo pessoal, e que baixar contraria os termos do YouTube
- [x] 7.5 Escrever os 10 links nas listas e atualizar os comentários que afirmavam lacuna sem saída

## 8. Verificação

- [x] 8.1 Testar a interpretação de trechos válidos e inválidos
- [x] 8.2 Recortar de uma fonte sintética e conferir duração exata, escala e codec dos dois formatos
- [x] 8.3 Baixar de verdade e conferir o clipe: 4,00s, 320x240, VP9 profile 0 e H.264 yuv420p
- [x] 8.4 Gerar um baralho de teste com palavra ausente, palavra do INES, frase e duas linhas malformadas
- [x] 8.5 Confirmar que 3 clipes da mesma URL geram 1 download só
- [x] 8.6 Confirmar que o link vai para o primeiro sinal em homônimo e que variante não dispara o aviso
- [x] 8.7 Gerar o baralho completo e confirmar `falta-video` de 20 para 9, sem falhas e sem clipe longo
- [ ] 8.8 Reimportar no Anki e conferir que as 10 palavras ganharam vídeo sem perder histórico, no desktop e no AnkiMobile — **passo manual no app**
