"""Modelo de nota do Anki e os templates de card.

Uma nota por sinal gera até dois cards. Não são notas separadas: assim,
acrescentar uma palavra é uma entrada só, corrigir a descrição corrige os dois
cards, e o *bury siblings* do Anki impede que os irmãos caiam no mesmo dia — o
que seria trapaça, já que responder um entrega o outro.

    Recepção   vídeo → palavra      reconhecer alguém sinalizando
    Produção   palavra → vídeo      saber fazer o sinal

Sem vídeo, o campo `Videos` já vem com o aviso escrito no lugar dele (ver
`html_videos`), então os dois cards continuam existindo — só mostram o aviso
em vez do vídeo.

A gramática (frase PT ↔ glosa) existe só para frases, no `MODELO_FRASE` mais
abaixo — o card de palavra isolada não carrega mais exemplo, glosa, classe
gramatical nem configuração de mão.
"""

import hashlib

import genanki

# IDs fixos: mudar isso faz o Anki tratar como modelo/baralho novo na
# reimportação, o que duplicaria tudo.
ID_MODELO = 1748203391
ID_BARALHO = 1748203392
NOME_BARALHO = "LIBRAS"

CAMPOS = [
    "Palavra",
    "Videos",
    "Descricao",
    "Origem",
    "Observacao",
]

CSS = """
.card {
  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", system-ui, sans-serif;
  font-size: 20px;
  line-height: 1.5;
  text-align: center;
  color: #1a1a1a;
  background: #fff;
  padding: 16px;
}
.rotulo {
  font-size: 12px; text-transform: uppercase; letter-spacing: .1em;
  color: #8a8a8a; margin-bottom: 14px;
}
.palavra { font-size: 32px; font-weight: 600; letter-spacing: .01em; }
.descricao { font-size: 17px; color: #444; margin-top: 14px; }
.exemplo { font-size: 17px; color: #555; font-style: italic; margin-top: 12px; }
.glosa {
  font-size: 19px; color: #16507c; font-weight: 600; letter-spacing: .03em;
  margin-top: 12px;
}
.meta { font-size: 13px; color: #999; margin-top: 12px; }
.variante { font-size: 12px; text-transform: uppercase; letter-spacing: .08em;
  color: #8a8a8a; margin: 10px 0 4px; }
.aviso {
  font-size: 14px; color: #8a5a00; background: #fff6e0;
  border-left: 3px solid #e0a800; padding: 8px 12px; margin-top: 14px;
  text-align: left; border-radius: 2px;
}
video { max-width: 100%; height: auto; border-radius: 4px; }
hr { border: none; border-top: 1px solid #e0e0e0; margin: 18px 0; }

.nightMode.card { color: #e8e8e8; background: #2c2c2c; }
.nightMode .descricao { color: #c8c8c8; }
.nightMode .exemplo { color: #bdbdbd; }
.nightMode .glosa { color: #7fb8e8; }
.nightMode .aviso { color: #f0c674; background: #3a3320; border-left-color: #b8860b; }
.nightMode hr { border-top-color: #4a4a4a; }
"""

TEMPLATES = [
    {
        "name": "Recepcao",
        "qfmt": '<div class="rotulo">Que palavra é esta?</div>\n{{Videos}}',
        "afmt": (
            '{{FrontSide}}\n<hr>\n'
            '<div class="palavra">{{Palavra}}</div>\n'
            '<div class="descricao">{{Descricao}}</div>\n'
            '{{#Observacao}}<div class="aviso">{{Observacao}}</div>{{/Observacao}}'
        ),
    },
    {
        "name": "Producao",
        "qfmt": (
            '<div class="rotulo">Faça o sinal</div>\n'
            '<div class="palavra">{{Palavra}}</div>'
        ),
        "afmt": (
            '{{FrontSide}}\n<hr>\n{{Videos}}\n'
            '{{#Origem}}<div class="meta">origem: {{Origem}}</div>{{/Origem}}\n'
            '{{#Observacao}}<div class="aviso">{{Observacao}}</div>{{/Observacao}}'
        ),
    },
]

MODELO = genanki.Model(
    ID_MODELO,
    "LIBRAS (INES)",
    fields=[{"name": nome} for nome in CAMPOS],
    templates=TEMPLATES,
    css=CSS,
)


ID_MODELO_FRASE = 1748203393

CAMPOS_FRASE = ["Frase", "Glosa", "Vocabulario", "Ausentes", "Observacao"]

# Frases não têm vídeo próprio: o INES é um dicionário de palavras. Então não
# existe card de recepção aqui — não há um sinal único para reconhecer. Sobram
# "sinalize a frase" (com os vídeos do vocabulário no verso) e a gramática.
TEMPLATES_FRASE = [
    {
        "name": "Sinalizar",
        "qfmt": '<div class="rotulo">Sinalize esta frase</div>\n'
                '<div class="exemplo">{{Frase}}</div>',
        "afmt": (
            '{{FrontSide}}\n<hr>\n'
            '{{#Glosa}}<div class="glosa">{{Glosa}}</div>{{/Glosa}}\n'
            '{{#Vocabulario}}<div class="meta">vocabulário</div>{{Vocabulario}}{{/Vocabulario}}\n'
            '{{#Ausentes}}<div class="aviso">Sem sinal no INES: {{Ausentes}}</div>{{/Ausentes}}\n'
            '{{#Observacao}}<div class="aviso">{{Observacao}}</div>{{/Observacao}}'
        ),
    },
    {
        "name": "Gramatica",
        "qfmt": (
            "{{#Glosa}}\n"
            '<div class="rotulo">Como fica em LIBRAS?</div>\n'
            '<div class="exemplo">{{Frase}}</div>\n'
            "{{/Glosa}}"
        ),
        "afmt": (
            '{{FrontSide}}\n<hr>\n'
            '<div class="meta">português</div>\n'
            '<div class="exemplo">{{Frase}}</div>\n'
            '<div class="meta">LIBRAS</div>\n'
            '<div class="glosa">{{Glosa}}</div>'
        ),
    },
]

MODELO_FRASE = genanki.Model(
    ID_MODELO_FRASE,
    "LIBRAS Frase (INES)",
    fields=[{"name": nome} for nome in CAMPOS_FRASE],
    templates=TEMPLATES_FRASE,
    css=CSS,
)


ID_MODELO_CONTRASTE = 1748203394

CAMPOS_CONTRASTE = ["Numero", "Titulo", "Videos", "Explicacao", "Observacao"]

# Números não são vocabulário isolado: a mesma configuração de mão muda de
# sentido pelo movimento (ordinal trêmulo, cardinal parado, quantidade própria).
# Um card "3 -> vídeo" ensinaria uma das formas e esconderia as outras duas.
TEMPLATES_CONTRASTE = [
    {
        "name": "Contraste",
        "qfmt": (
            '<div class="rotulo">{{Titulo}}</div>\n'
            '<div class="palavra">{{Numero}}</div>\n'
            "{{Videos}}"
        ),
        "afmt": (
            '{{FrontSide}}\n<hr>\n'
            '<div class="descricao">{{Explicacao}}</div>\n'
            '{{#Observacao}}<div class="aviso">{{Observacao}}</div>{{/Observacao}}'
        ),
    }
]

MODELO_CONTRASTE = genanki.Model(
    ID_MODELO_CONTRASTE,
    "LIBRAS Número (INES)",
    fields=[{"name": nome} for nome in CAMPOS_CONTRASTE],
    templates=TEMPLATES_CONTRASTE,
    css=CSS,
)


def guid_numero(chave):
    digest = hashlib.sha1(f"numero:{chave}".encode("utf-8")).hexdigest()
    return genanki.guid_for(digest)


def criar_nota_contraste(numero, titulo, blocos, explicacao,
                         observacao="", tags=(), chave=None):
    """Card de contraste: vídeos rotulados na frente, explicação no verso."""
    partes = []
    for rotulo, mp4, webm in blocos:
        partes.append(f'<div class="variante">{rotulo}</div>')
        partes.append(html_video(mp4, webm) if mp4 else "")
    return genanki.Note(
        model=MODELO_CONTRASTE,
        guid=guid_numero(chave or numero),
        fields=[numero, titulo, "".join(partes), explicacao, observacao],
        tags=sorted(tags),
    )


def guid_para(ident, video):
    """GUID estável da nota.

    Deriva de `ident` (identificador interno do INES, estável) mais o nome do
    vídeo. O campo `id` NÃO entra: ele é posicional na ordem alfabética, então
    uma palavra nova publicada em "A" deslocaria todos os `id` e duplicaria o
    baralho inteiro na reimportação seguinte.

    O nome do vídeo desempata as colisões de `ident` que existem na base.
    """
    digest = hashlib.sha1(f"ines:{ident}:{video}".encode("utf-8")).hexdigest()
    return genanki.guid_for(digest)


def html_video(mp4, webm=None):
    """Um `<video>` com os dois formatos; cada plataforma pega o que decodifica.

    O webview do Anki desktop não decodifica H.264, então o WebM vem primeiro.
    `playsinline` evita que o iOS abra em tela cheia a cada card.
    """
    fontes = []
    if webm:
        fontes.append(f'<source src="{webm}" type="video/webm">')
    fontes.append(f'<source src="{mp4}" type="video/mp4">')
    return "<video autoplay loop muted playsinline>" + "".join(fontes) + "</video>"


SEM_VIDEO = '<div class="aviso">Sem vídeo disponível — grave na aula.</div>'


def html_videos(pares):
    """Monta o bloco de vídeos. Sem vídeo, escreve o aviso no lugar dele.

    Assim o aviso aparece exatamente onde o vídeo apareceria, em vez de deixar
    o card com um espaço vazio.
    """
    if not pares:
        return SEM_VIDEO
    if len(pares) == 1:
        mp4, webm = pares[0]
        return html_video(mp4, webm)
    partes = []
    for i, (mp4, webm) in enumerate(pares, start=1):
        partes.append(f'<div class="variante">variante {i}</div>')
        partes.append(html_video(mp4, webm))
    return "".join(partes)


def html_vocabulario(itens):
    """Bloco de vídeos do vocabulário de uma frase, cada um sob sua palavra."""
    partes = []
    for palavra, mp4, webm in itens:
        partes.append(f'<div class="variante">{palavra}</div>')
        partes.append(html_video(mp4, webm))
    return "".join(partes)


def guid_frase(texto):
    """GUID de uma nota de frase, derivado do próprio texto em português.

    Assim, corrigir a glosa ou o vocabulário reconhecido atualiza a nota
    existente em vez de criar outra.
    """
    digest = hashlib.sha1(f"frase:{texto.strip().lower()}".encode("utf-8")).hexdigest()
    return genanki.guid_for(digest)


def criar_nota_frase(frase, glosa="", vocabulario=(), ausentes=(),
                     observacao="", tags=()):
    """Cria a nota de uma frase da apostila."""
    return genanki.Note(
        model=MODELO_FRASE,
        guid=guid_frase(frase),
        fields=[
            frase,
            glosa,
            html_vocabulario(vocabulario),
            ", ".join(ausentes),
            observacao,
        ],
        tags=sorted(tags),
    )


def criar_baralho(nome=NOME_BARALHO):
    return genanki.Deck(ID_BARALHO, nome)


def criar_nota(palavra, pares_video, descricao="", origem="", observacao="",
               tags=(), guid=None):
    """Cria a nota do Anki a partir dos dados já resolvidos."""
    return genanki.Note(
        model=MODELO,
        guid=guid,
        fields=[
            palavra,
            html_videos(pares_video),
            descricao,
            origem,
            observacao,
        ],
        tags=sorted(tags),
    )
