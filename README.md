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
```

Ao final vem um relatório do que entrou e do que precisa de atenção. Nada é descartado em silêncio.

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

Nem toda palavra da frase tem sinal no INES. As que não têm ficam de fora do vocabulário do verso e entram, em vez disso, num aviso: "Sem sinal no INES: ...". Exemplo real do baralho — a frase "Vocês estão aprendendo Libras." mostra os vídeos de VOCÊ, ESTAR e APRENDER, mas "Libras" vai para o aviso porque a própria palavra "Libras" não é verbete do dicionário.

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

### Tags para filtrar no Anki

| Tag | O que é |
|---|---|
| `falta-video` | sem vídeo no INES — grave na aula |
| `composto` | sem verbete próprio; o card mostra os componentes em sequência |
| `confirmar-sinal` | a escolha do componente saiu por eliminação — confirme na aula |
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
├── modelo.py     modelos de nota e templates dos cards
├── listas.py     leitura das listas de estudo
├── numeros.py    regras dos números 1–10
├── gerador.py    montagem do baralho e relatório
└── cli.py        linha de comando

listas/           suas listas de estudo
out/              baralhos gerados
.cache/           dicionário e vídeos baixados (não versionar)
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

O dicionário tem lacunas e alguns erros — o projeto trata isso explicitamente em vez de esconder. Palavras sem material viram cards marcados em vez de sumirem em silêncio, e verbetes com dado inconsistente recebem aviso. O raciocínio por trás de cada tratamento está em `openspec/changes/libras-anki-deck/design.md`.

Dois detalhes que valem saber ao estudar:

- Os MP4 do INES são H.264, que o webview do Anki desktop não decodifica. Cada vídeo também é convertido para WebM e o card leva os dois formatos, deixando cada plataforma escolher.
- Nem toda "lacuna" é falha do dicionário. `BOM DIA` não existe como verbete porque se sinaliza BOM + DIA em sequência; `ela` não existe porque em LIBRAS o pronome de 3ª pessoa é apontar e não marca gênero — é o mesmo sinal de `ELE`.
