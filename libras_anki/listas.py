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

O tipo da linha sai do prefixo `=` e da consulta ao dicionário, nada mais.
"""

from .indice import palavras_da_frase

FORCAR_PALAVRA = "="

TIPO_PALAVRA = "palavra"
TIPO_FRASE = "frase"


class Item:
    """Uma linha de lista já interpretada."""

    def __init__(self, texto, tipo, origem="", linha=0):
        self.texto = texto
        self.tipo = tipo
        self.origem = origem
        self.linha = linha

    def __repr__(self):
        return f"<Item {self.tipo} {self.texto!r}>"


def _interpretar(bruto, indice, origem, numero):
    """Decide se a linha é palavra ou frase, resolvendo contra o dicionário."""
    texto = bruto.strip()

    if texto.startswith(FORCAR_PALAVRA):
        return Item(texto[1:].strip(), TIPO_PALAVRA, origem, numero)

    # Entradas do INES com espaço existem ("TUDO BEM", "COM LICENÇA", "POR
    # FAVOR"), então não dá para decidir por espaço. Quem decide é o dicionário:
    # se a linha inteira resolve como verbete, é palavra.
    if indice.resolver(texto):
        return Item(texto, TIPO_PALAVRA, origem, numero)

    # Não resolveu: se tem mais de uma palavra significativa, é frase.
    if len(palavras_da_frase(texto)) > 1:
        return Item(texto, TIPO_FRASE, origem, numero)

    return Item(texto, TIPO_PALAVRA, origem, numero)


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
