"""Download, conversão e cache dos vídeos dos sinais.

Só os vídeos das palavras efetivamente pedidas são baixados. Cada arquivo tem
entre 23 e 52 KB, então um baralho de algumas centenas de sinais fica na casa
dos poucos megabytes.

Os MP4 do INES são H.264, que o webview do Anki desktop não decodifica — o
player renderiza vazio mesmo com o arquivo íntegro. Por isso cada vídeo também é
convertido para WebM/VP9 e o card leva os dois formatos em `<source>` separados,
deixando cada plataforma escolher (ver decisão 8 do design).

O campo `image` dos verbetes é ignorado de propósito: o diretório
`public/media/palavras/images/` do INES responde 404 — as imagens estáticas não
existem mais no servidor, só os vídeos.

Parte dos verbetes declara nome de arquivo que o servidor não entrega, com o
arquivo certo lá sob outro sufixo numérico — `JUNHO` aponta `junho1Sm` e quem
responde é `junhoSm`. Quando o download falha, as variantes de sufixo são
tentadas, e só é aceita a que nenhum outro verbete declarar como sua: sem essa
guarda `SER2` (que aponta `ser3Sm`, 404) pegaria `ser1Sm`, o vídeo de `SER1`,
mostrando um sinal por outro.
"""

import re
import subprocess

import requests

from . import config

TAG_FALTA_VIDEO = "falta-video"
TAG_VIDEO_RENOMEADO = "video-renomeado"

# Nome de vídeo do INES partido em prefixo, sufixo numérico e cauda:
# "junho1Sm_Prog001.mp4" -> ("junho", "1", "Sm_Prog001.mp4"). O sufixo é o que a
# base erra, e o resto do nome é o que identifica a palavra.
_NOME_VIDEO = re.compile(r"^(.+?)(\d*)(Sm_Prog\d+\.mp4)$")

# Sufixos tentados quando o declarado não responde. A base não passa de 3
# verbetes homônimos com vídeo, então não vale varrer além disso.
_SUFIXOS = ("", "1", "2", "3")

# -crf 32 -b:v 0 é VP9 em qualidade constante; nos vídeos do INES (240x176) sai
# menor que o MP4 original. -an descarta áudio, que esses vídeos não têm.
# `yuv420p` fixo porque VP9 4:4:4 é profile 1, e nem todo webview decodifica
# profile diferente de 0. As fontes do INES já são 4:2:0; as de fora nem sempre.
ARGS_VP9 = ["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-pix_fmt", "yuv420p", "-an"]

# H.264 para o iOS, que não decodifica WebM. `yuv420p` e `+faststart` porque o
# WKWebView recusa alguns pixel formats e gosta do moov no começo do arquivo.
ARGS_H264 = [
    "-c:v", "libx264", "-preset", "medium", "-crf", "28",
    "-pix_fmt", "yuv420p", "-movflags", "+faststart", "-an",
]


def caminho_ffmpeg():
    """Caminho do ffmpeg empacotado; None se a dependência não estiver instalada."""
    try:
        import imageio_ffmpeg
    except ImportError:
        return None
    return imageio_ffmpeg.get_ffmpeg_exe()


class Midia:
    """Baixa e cacheia vídeos, registrando o que falhou."""

    def __init__(self, sessao=None, declarados=()):
        self.sessao = sessao or requests.Session()
        self.falhas = {}
        self.baixados = 0
        self.do_cache = 0
        self.convertidos = 0
        self.webm_do_cache = 0
        self.falhas_conversao = {}
        self._ffmpeg = None
        # Todo nome de arquivo que algum verbete declara. Serve de guarda na
        # recuperação por sufixo: um nome que já tem dono não pode ser
        # emprestado, porque é o vídeo de outro sinal.
        self.declarados = frozenset(declarados)
        # nome declarado -> nome que respondeu, para a tag e o relatório.
        self.renomeados = {}

    def _obter_ffmpeg(self):
        """Caminho do ffmpeg empacotado, memorizado entre chamadas."""
        if self._ffmpeg is None:
            self._ffmpeg = caminho_ffmpeg() or False
        return self._ffmpeg or None

    def converter_webm(self, mp4):
        """Converte um MP4 para WebM/VP9, com cache. Devolve o caminho ou None."""
        destino = mp4.with_suffix(".webm")
        if destino.exists() and destino.stat().st_size > 0:
            self.webm_do_cache += 1
            return destino

        ffmpeg = self._obter_ffmpeg()
        if ffmpeg is None:
            self.falhas_conversao[mp4.name] = "imageio-ffmpeg não instalado"
            return None

        temporario = destino.with_suffix(".webm.tmp.webm")
        resultado = subprocess.run(
            [ffmpeg, "-y", "-v", "error", "-i", str(mp4), *ARGS_VP9, str(temporario)],
            capture_output=True,
            text=True,
        )
        if resultado.returncode != 0 or not temporario.exists():
            self.falhas_conversao[mp4.name] = (resultado.stderr or "ffmpeg falhou")[:200]
            temporario.unlink(missing_ok=True)
            return None

        temporario.replace(destino)
        self.convertidos += 1
        return destino

    def obter_par(self, nome):
        """Devolve (mp4, webm) para um vídeo; webm pode ser None se a conversão falhar.

        O card usa os dois: WebM para o webview do Anki desktop, MP4 para o iOS.
        """
        mp4 = self.obter(nome)
        if mp4 is None:
            return None, None
        return mp4, self.converter_webm(mp4)

    def variantes(self, nome):
        """Nomes com o sufixo numérico trocado, sem os que já têm dono.

        A base erra esse sufixo com frequência e o arquivo certo está no
        servidor sob outro número. Um candidato declarado por outro verbete é
        descartado aqui: ele é o vídeo de outro sinal, não uma correção deste.
        """
        partes = _NOME_VIDEO.match(nome)
        if not partes:
            return []
        prefixo, sufixo, cauda = partes.groups()
        return [
            candidato
            for outro in _SUFIXOS
            if outro != sufixo
            for candidato in [f"{prefixo}{outro}{cauda}"]
            if candidato not in self.declarados
        ]

    def obter(self, nome):
        """Devolve o caminho local do vídeo, ou None se não foi possível obter."""
        if nome in self.falhas:
            return None

        config.CACHE_VIDEOS.mkdir(parents=True, exist_ok=True)
        caminho = self._do_cache(nome)
        if caminho:
            return caminho

        caminho = self._baixar(nome)
        if caminho:
            return caminho

        # Só agora, com o nome declarado comprovadamente sem resposta, as
        # variantes entram. Sondar o cache antes disto seria pior que inútil:
        # AGOSTO1 e AGOSTO2 são variantes um do outro, e o arquivo recuperado
        # para o primeiro atenderia o segundo sem que o vídeo dele — que
        # funciona — chegasse a ser pedido. É também o que faz a nota voltar
        # sozinha ao vídeo dela se o INES corrigir o cadastro.
        for alternativo in self.variantes(nome):
            caminho = self._do_cache(alternativo) or self._baixar(
                alternativo, registrar_falha=False
            )
            if caminho:
                self.renomeados[nome] = alternativo
                del self.falhas[nome]
                return caminho
        return None

    def _do_cache(self, nome):
        """Caminho do vídeo já em cache, ou None."""
        destino = config.CACHE_VIDEOS / nome
        if destino.exists() and destino.stat().st_size > 0:
            self.do_cache += 1
            return destino
        return None

    def _baixar(self, nome, registrar_falha=True):
        """Baixa um vídeo para o cache. Devolve o caminho ou None.

        `registrar_falha` fica falso ao sondar variantes: elas são palpite, e o
        404 de um palpite não é pendência que interesse ao relatório.
        """
        try:
            resposta = self.sessao.get(config.URL_VIDEOS + nome, timeout=config.TIMEOUT)
            resposta.raise_for_status()
        except requests.RequestException as erro:
            if registrar_falha:
                self.falhas[nome] = str(erro)
            return None

        if not resposta.content:
            if registrar_falha:
                self.falhas[nome] = "resposta vazia"
            return None

        # Grava via temporário para não deixar arquivo truncado no cache se a
        # escrita for interrompida.
        destino = config.CACHE_VIDEOS / nome
        temporario = destino.with_suffix(destino.suffix + ".tmp")
        temporario.write_bytes(resposta.content)
        temporario.replace(destino)
        self.baixados += 1
        return destino

    def obter_muitos(self, nomes):
        """Devolve (caminhos_ok, nomes_que_falharam) para uma lista de vídeos."""
        caminhos, faltando = [], []
        for nome in nomes:
            caminho = self.obter(nome)
            if caminho is None:
                faltando.append(nome)
            else:
                caminhos.append(caminho)
        return caminhos, faltando

    def resumo(self):
        return {
            "baixados": self.baixados,
            "do_cache": self.do_cache,
            "convertidos": self.convertidos,
            "webm_do_cache": self.webm_do_cache,
            "falhas": dict(self.falhas),
            "falhas_conversao": dict(self.falhas_conversao),
        }
