"""Leitura das listas de estudo.

Cada arquivo em `listas/` é um agrupamento temático mantido por você. O
agrupamento NÃO vem do campo `assunto` do INES: os 21 assuntos de lá são
categorias concretas (ALIMENTO, ANIMAL, CORPO…), 64% dos verbetes caem em
"NENHUM", e não existe nada como "saudações". Filtrar possessivos por classe
gramatical também falha — `PRON. POSS.` tem só NOSSO e SEU, enquanto MEU1/MEU2
estão classificados como PRONOME.

Formato de cada linha:

    casa                          palavra
    tudo bem                      palavra (o INES tem verbetes com espaço)
    Meu carro é vermelho          frase
    = bom dia                     força tratar como palavra, mesmo sem verbete
    # comentário                  ignorado

    terça-feira @yt https://youtu.be/AAA 1:23-1:27    vídeo de fora do INES

O tipo da linha sai do prefixo `=` e da consulta ao dicionário, nada mais. O
`@yt` é separado antes disso, para que a URL não conte como palavra na hora de
decidir se a linha é frase (ver `youtube.py` para a sintaxe do intervalo).
"""

from . import youtube
from .indice import palavras_da_frase

FORCAR_PALAVRA = "="
MARCADOR_VIDEO = youtube.MARCADOR

TIPO_PALAVRA = "palavra"
TIPO_FRASE = "frase"


class Item:
    """Uma linha de lista já interpretada."""

    def __init__(self, texto, tipo, origem="", linha=0, video=None, problema=None):
        self.texto = texto
        self.tipo = tipo
        self.origem = origem
        self.linha = linha
        # Vídeo de fonte externa declarado com `@yt`, se houver.
        self.video = video
        # Erro de escrita da própria linha, para o relatório. Uma URL torta não
        # derruba o baralho inteiro: a linha vira card sem o vídeo, e o problema
        # aparece no fim para você corrigir.
        self.problema = problema

    @property
    def local(self):
        return f"{self.origem}.txt:{self.linha}"

    def __repr__(self):
        return f"<Item {self.tipo} {self.texto!r}>"


def _separar_video(texto):
    """Tira o `@yt <url> [trecho]` do fim da linha. Devolve (texto, video, erro)."""
    if MARCADOR_VIDEO not in texto:
        return texto, None, None

    antes, _, resto = texto.partition(MARCADOR_VIDEO)
    campos = resto.split()
    if not campos:
        return antes.strip(), None, f"{MARCADOR_VIDEO} sem URL"

    try:
        video = youtube.VideoExterno(campos[0], campos[1] if len(campos) > 1 else None)
    except youtube.ErroVideoExterno as erro:
        return antes.strip(), None, str(erro)
    return antes.strip(), video, None


def _interpretar(bruto, indice, origem, numero):
    """Decide se a linha é palavra ou frase, resolvendo contra o dicionário."""
    texto, video, problema = _separar_video(bruto.strip())

    def item(conteudo, tipo):
        return Item(conteudo, tipo, origem, numero, video, problema)

    if texto.startswith(FORCAR_PALAVRA):
        return item(texto[1:].strip(), TIPO_PALAVRA)

    # Entradas do INES com espaço existem ("TUDO BEM", "COM LICENÇA", "POR
    # FAVOR"), então não dá para decidir por espaço. Quem decide é o dicionário:
    # se a linha inteira resolve como verbete, é palavra.
    if indice.resolver(texto):
        return item(texto, TIPO_PALAVRA)

    # Não resolveu: se tem mais de uma palavra significativa, é frase.
    if len(palavras_da_frase(texto)) > 1:
        return item(texto, TIPO_FRASE)

    return item(texto, TIPO_PALAVRA)


def ler(caminho, indice):
    """Lê um arquivo de lista e devolve os itens interpretados."""
    itens = []
    with open(caminho, encoding="utf-8") as arquivo:
        for numero, bruto in enumerate(arquivo, start=1):
            linha = bruto.strip()
            if not linha or linha.startswith("#"):
                continue
            itens.append(_interpretar(linha, indice, caminho.stem, numero))
    return itens


def ler_muitas(caminhos, indice):
    """Lê vários arquivos, mantendo a ordem e removendo repetições."""
    itens, vistos = [], set()
    for caminho in caminhos:
        for item in ler(caminho, indice):
            chave = (item.tipo, item.texto.strip().lower())
            if chave in vistos:
                continue
            vistos.add(chave)
            itens.append(item)
    return itens
