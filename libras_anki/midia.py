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
"""

import subprocess

import requests

from . import config

TAG_FALTA_VIDEO = "falta-video"

# -crf 32 -b:v 0 é VP9 em qualidade constante; nos vídeos do INES (240x176) sai
# menor que o MP4 original. -an descarta áudio, que esses vídeos não têm.
ARGS_VP9 = ["-c:v", "libvpx-vp9", "-crf", "32", "-b:v", "0", "-an"]


class Midia:
    """Baixa e cacheia vídeos, registrando o que falhou."""

    def __init__(self, sessao=None):
        self.sessao = sessao or requests.Session()
        self.falhas = {}
        self.baixados = 0
        self.do_cache = 0
        self.convertidos = 0
        self.webm_do_cache = 0
        self.falhas_conversao = {}
        self._ffmpeg = None

    def _obter_ffmpeg(self):
        """Caminho do ffmpeg empacotado; None se a dependência não estiver instalada."""
        if self._ffmpeg is None:
            try:
                import imageio_ffmpeg
            except ImportError:
                self._ffmpeg = False
            else:
                self._ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
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

    def obter(self, nome):
        """Devolve o caminho local do vídeo, ou None se não foi possível obter."""
        if nome in self.falhas:
            return None

        config.CACHE_VIDEOS.mkdir(parents=True, exist_ok=True)
        destino = config.CACHE_VIDEOS / nome
        if destino.exists() and destino.stat().st_size > 0:
            self.do_cache += 1
            return destino

        try:
            resposta = self.sessao.get(config.URL_VIDEOS + nome, timeout=config.TIMEOUT)
            resposta.raise_for_status()
        except requests.RequestException as erro:
            self.falhas[nome] = str(erro)
            return None

        if not resposta.content:
            self.falhas[nome] = "resposta vazia"
            return None

        # Grava via temporário para não deixar arquivo truncado no cache se a
        # escrita for interrompida.
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
