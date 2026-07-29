"""Agrupamento de verbetes em sinais, e marcação de anomalias da base.

O sufixo numérico do INES ("ABANDONAR1", "ABANDONAR2") não significa sempre a
mesma coisa. Medição sobre os 604 grupos existentes:

     96 (16%)  descricao E classe idênticas   -> variantes do mesmo sinal
    481 (80%)  descricoes todas diferentes    -> homônimos, sentidos distintos
     27 ( 4%)  misto

Juntar homônimos num card só ensinaria, por exemplo, que OBRIGADO1 (grato) e
OBRIGADO2 (que tem o dever) são dois jeitos de agradecer — o que é falso.
"""

import re
import unicodedata
from collections import defaultdict

from .indice import normalizar, raiz

TAG_GRUPO_MISTO = "grupo-misto"
TAG_VIDEO_SUSPEITO = "video-suspeito"

SIMPLES = "simples"
VARIANTE = "variante"
HOMONIMO = "homonimo"


class Sinal:
    """Um sinal que vira uma nota do Anki.

    Uma variante reúne mais de um verbete (vários vídeos no mesmo card); um
    homônimo vira um Sinal por verbete, cada um com sua própria descrição.
    """

    def __init__(self, verbetes, tipo, tags=()):
        self.verbetes = list(verbetes)
        self.tipo = tipo
        self.tags = set(tags)

    @property
    def principal(self):
        return self.verbetes[0]

    @property
    def palavra(self):
        """Nome exibido: sem o sufixo numérico quando é variante do mesmo sinal."""
        bruta = self.principal["palavra"]
        return raiz(bruta) if self.tipo == VARIANTE else bruta

    @property
    def ident(self):
        return self.principal["ident"]

    @property
    def videos(self):
        return [v["video"] for v in self.verbetes if v.get("video")]

    @property
    def descricao(self):
        return self.principal.get("descricao", "")

    def __repr__(self):
        return f"<Sinal {self.palavra} {self.tipo} {len(self.verbetes)} verbete(s)>"


def _slug(palavra):
    """Aproxima o nome do arquivo de vídeo a partir da palavra.

    "CANA DE AÇÚCAR" -> "cana-de-acucar", que casa com cana-de-acucarSm_Prog001.mp4.
    """
    texto = unicodedata.normalize("NFD", palavra.lower())
    texto = "".join(c for c in texto if unicodedata.category(c) != "Mn")
    return re.sub(r"[^a-z0-9]+", "-", texto).strip("-")


def _video_combina(palavra, video):
    """O nome do vídeo começa com o slug da palavra?"""
    if not video:
        return False
    prefixo = video.split("Sm_")[0].split("_Prog")[0]
    return _slug(prefixo) == _slug(palavra)


def resolver_ident_duplicado(verbetes):
    """Descarta linhas cujo vídeo pertence claramente a outra palavra.

    Duas colisões de `ident` existem na base ativa e ambas têm a mesma forma:
    uma linha correta e outra apontando para o vídeo de outro verbete.

        ident 1438  CHINELO -> chineloSm_...  (ok)   / chilenoSm_...  (é CHILENO)
        ident 2484  DOIS2   -> dois2Sm_...    (ok)   / doar2Sm_...    (é DOAR2)

    Quando nenhuma linha do grupo casa pelo prefixo, todas são mantidas: o
    desempate passa a ser o nome do vídeo, que torna os GUIDs distintos.
    """
    por_ident = defaultdict(list)
    for verbete in verbetes:
        por_ident[verbete["ident"]].append(verbete)

    mantidos, descartados = [], []
    for grupo in por_ident.values():
        if len(grupo) == 1:
            mantidos.extend(grupo)
            continue
        combinam = [v for v in grupo if _video_combina(v["palavra"], v.get("video"))]
        if combinam and len(combinam) < len(grupo):
            mantidos.extend(combinam)
            descartados.extend(v for v in grupo if v not in combinam)
        else:
            mantidos.extend(grupo)
    return mantidos, descartados


def classificar(verbetes):
    """Agrupa verbetes por raiz e devolve a lista de Sinais."""
    por_raiz = defaultdict(list)
    for verbete in verbetes:
        por_raiz[raiz(normalizar(verbete["palavra"]))].append(verbete)

    sinais = []
    for grupo in por_raiz.values():
        if len(grupo) == 1:
            sinais.append(Sinal(grupo, SIMPLES))
            continue

        descricoes = {v.get("descricao", "") for v in grupo}
        classes = {v.get("classe") for v in grupo}

        if len(descricoes) == 1 and len(classes) == 1:
            # Mesmo sentido e mesma classe: variantes do mesmo sinal.
            sinais.append(Sinal(grupo, VARIANTE))
        elif len(descricoes) == len(grupo):
            # Todos com sentido próprio: homônimos.
            sinais.extend(Sinal([v], HOMONIMO) for v in grupo)
        else:
            # Parte igual, parte diferente: separa e sinaliza para conferência.
            sinais.extend(Sinal([v], HOMONIMO, {TAG_GRUPO_MISTO}) for v in grupo)

    return sinais


def marcar_videos_compartilhados(sinais):
    """Marca com `video-suspeito` sinais que dividem um vídeo com outro sinal.

    Nem todo compartilhamento é erro — em LIBRAS o mesmo sinal serve para verbo e
    substantivo relacionado (CHEIRAR/CHEIRO1, COMUNGAR/COMUNHÃO). Distinguir isso
    automaticamente exigiria entender relação semântica, então a decisão fica com
    quem estuda: a nota é marcada e listada no relatório.
    """
    dono = defaultdict(set)
    for sinal in sinais:
        for video in sinal.videos:
            dono[video].add(id(sinal))

    compartilhados = {v for v, s in dono.items() if len(s) > 1}
    afetados = []
    for sinal in sinais:
        if any(v in compartilhados for v in sinal.videos):
            sinal.tags.add(TAG_VIDEO_SUSPEITO)
            afetados.append(sinal)
    return afetados


def construir(verbetes):
    """Pipeline completo: dedup por ident, classificação e marcação de anomalias."""
    mantidos, descartados = resolver_ident_duplicado(verbetes)
    sinais = classificar(mantidos)
    suspeitos = marcar_videos_compartilhados(sinais)
    return sinais, {"descartados": descartados, "video_suspeito": suspeitos}
