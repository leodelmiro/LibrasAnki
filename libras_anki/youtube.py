"""Vídeos de fonte externa: YouTube e o que mais o yt-dlp suportar.

O INES é um dicionário generoso, mas tem lacunas reais — TERÇA-FEIRA, TELEFONE,
PAMONHA — e para elas o baralho só sabia dizer "grave na aula". Quando existe um
vídeo do sinal em algum canal, ele resolve a lacuna hoje. E quando o vídeo do
INES existe mas você prefere outro, o link tem prioridade: quem estuda sabe qual
sinal quer decorar.

Nas listas, o link vem depois da palavra, atrás do marcador `@yt`:

    terça-feira  @yt https://youtu.be/AAA 1:23-1:27
    telefone     @yt https://youtu.be/BBB 0:41+3

O intervalo é `início-fim` ou `início+duração`, em `M:SS`, `H:MM:SS` ou
segundos. Sem intervalo, o vídeo inteiro vira o clipe — o que só faz sentido se
o link já for um clipe curto.

Um vídeo de aula de dez minutos rende dezenas de sinais, então o download fica
em `.cache/externos/` e cada clipe é recortado dele; só o primeiro sinal de cada
vídeo paga a rede.

Os dois formatos saem daqui pela mesma razão descrita em `midia.py`: WebM/VP9
porque o webview do Anki desktop não decodifica H.264, e MP4/H.264 porque o iOS
não decodifica WebM. Um clipe de aula vem em 720p e pesaria muito mais que os
240x176 do INES, então a escala é limitada a 480 px de largura.
"""

import hashlib
import re
import subprocess

from . import config, midia

MARCADOR = "@yt"
TAG = "video-externo"

# Acima disso quase certamente é um vídeo inteiro entrando no baralho por
# esquecimento do intervalo — o clipe é gerado assim mesmo, com aviso.
SEGUNDOS_SUSPEITOS = 30

# Aspas simples são interpretadas pelo próprio ffmpeg no filtergraph, não pelo
# shell: protegem a vírgula de `min()`, que separaria argumentos do filtro.
FILTRO_ESCALA = "scale=w='min(480,iw)':h=-2"

# AV1 é excluído de propósito: alguns builds do ffmpeg empacotado decodificam
# devagar ou não decodificam, e sempre há um VP9 ou H.264 equivalente no YouTube.
FORMATO = (
    "bv*[vcodec!*=av01][height<=720]/bv*[height<=720]/"
    "b[height<=720]/bv*/b"
)

# Alguns vídeos públicos respondem "This video is not available" ao client padrão
# e abrem normalmente pelo do Android — dois canais de LIBRAS usados aqui caíram
# nisso. Listar os dois faz o yt-dlp tentar em ordem em vez de desistir no
# primeiro. Não é contornar restrição: são vídeos abertos, é incompatibilidade de
# client mesmo.
CLIENTES = ["default", "android"]

_TEMPO = re.compile(r"^(?:(\d+):)?(?:(\d+):)?(\d+(?:\.\d+)?)$")
_DURACAO = re.compile(r"Duration:\s*(\d+):(\d+):(\d+(?:\.\d+)?)")


class ErroVideoExterno(Exception):
    """Link ou intervalo escrito de forma que não dá para interpretar."""


def segundos(texto):
    """Converte `1:23`, `01:02:03`, `83` ou `1:23.5` em segundos."""
    casou = _TEMPO.match(texto.strip())
    if not casou:
        raise ErroVideoExterno(f"tempo inválido: {texto!r}")
    a, b, c = casou.groups()
    partes = [p for p in (a, b, c) if p is not None]
    total = 0.0
    for parte in partes:
        total = total * 60 + float(parte)
    return total


def interpretar_trecho(trecho):
    """Devolve (início, fim) em segundos. `fim` é None quando vai até o final."""
    if not trecho:
        return 0.0, None

    if "+" in trecho:
        inicio, _, duracao = trecho.partition("+")
        inicio = segundos(inicio)
        return inicio, inicio + segundos(duracao)

    if "-" in trecho:
        inicio, _, fim = trecho.partition("-")
        inicio, fim = segundos(inicio), segundos(fim)
        if fim <= inicio:
            raise ErroVideoExterno(f"o fim vem antes do início em {trecho!r}")
        return inicio, fim

    # Só um tempo: começa ali e vai até o final do vídeo.
    return segundos(trecho), None


def duracao_de(caminho):
    """Duração do arquivo em segundos, lida do ffmpeg. None se não der para ler.

    Serve para conferir o clipe pronto: sem intervalo no `@yt`, o vídeo inteiro
    vira o clipe, e só depois de recortar dá para saber se isso foi um descuido
    ou um link que já era curto.
    """
    ffmpeg = midia.caminho_ffmpeg()
    if ffmpeg is None:
        return None
    resultado = subprocess.run(
        [ffmpeg, "-hide_banner", "-i", str(caminho)], capture_output=True, text=True
    )
    casou = _DURACAO.search(resultado.stderr)
    if not casou:
        return None
    horas, minutos, segundos_ = casou.groups()
    return int(horas) * 3600 + int(minutos) * 60 + float(segundos_)


def _formatar(t):
    return f"{int(t) // 60}:{t % 60:04.1f}".replace(".0", "")


class VideoExterno:
    """Um link com o trecho a recortar, já interpretado."""

    def __init__(self, url, trecho=None):
        if not re.match(r"^https?://", url):
            raise ErroVideoExterno(f"não parece uma URL: {url!r}")
        self.url = url
        self.trecho = trecho
        self.inicio, self.fim = interpretar_trecho(trecho)

    @property
    def duracao(self):
        return None if self.fim is None else self.fim - self.inicio

    @property
    def chave(self):
        """Identifica o clipe: mesma URL e mesmo trecho geram o mesmo arquivo."""
        crua = f"{self.url}|{self.inicio}|{self.fim}"
        return hashlib.sha1(crua.encode("utf-8")).hexdigest()[:12]

    @property
    def rotulo(self):
        if self.fim is None and not self.inicio:
            return self.url
        fim = "fim" if self.fim is None else _formatar(self.fim)
        return f"{self.url} {_formatar(self.inicio)}–{fim}"

    def __repr__(self):
        return f"<VideoExterno {self.rotulo}>"


class Externos:
    """Baixa, recorta e cacheia vídeos de fonte externa, registrando falhas."""

    def __init__(self):
        self.clipes = 0
        self.do_cache = 0
        self.fontes_baixadas = 0
        self.falhas = {}
        self.longos = []

    # -- download ----------------------------------------------------------

    def _procurar_fonte(self, base):
        candidatos = [
            p for p in base.parent.glob(base.name + ".*")
            if p.suffix != ".part" and p.stat().st_size > 0
        ]
        return candidatos[0] if candidatos else None

    def _fonte(self, url):
        """Baixa o vídeo inteiro uma vez só e devolve o caminho no cache."""
        config.CACHE_EXTERNOS.mkdir(parents=True, exist_ok=True)
        digest = hashlib.sha1(url.encode("utf-8")).hexdigest()[:12]
        base = config.CACHE_EXTERNOS / f"fonte-{digest}"

        achado = self._procurar_fonte(base)
        if achado:
            return achado

        try:
            import yt_dlp
        except ImportError:
            raise ErroVideoExterno(
                "yt-dlp não instalado — rode "
                ".venv/Scripts/python.exe -m pip install -r requirements.txt"
            )

        opcoes = {
            "outtmpl": str(base) + ".%(ext)s",
            "format": FORMATO,
            "quiet": True,
            "no_warnings": True,
            "noprogress": True,
            "noplaylist": True,
            "retries": 3,
            "extractor_args": {"youtube": {"player_client": CLIENTES}},
        }
        try:
            with yt_dlp.YoutubeDL(opcoes) as ydl:
                ydl.download([url])
        except Exception as erro:  # yt-dlp levanta uma família larga de erros
            raise ErroVideoExterno(str(erro).strip()[:200]) from erro

        achado = self._procurar_fonte(base)
        if achado is None:
            raise ErroVideoExterno("o yt-dlp terminou sem deixar arquivo")
        self.fontes_baixadas += 1
        return achado

    # -- recorte -----------------------------------------------------------

    def _cortar(self, fonte, video, destino, args):
        """Recorta o trecho e converte com `args`. Devolve o caminho ou levanta."""
        ffmpeg = midia.caminho_ffmpeg()
        if ffmpeg is None:
            raise ErroVideoExterno("imageio-ffmpeg não instalado")

        comando = [ffmpeg, "-y", "-v", "error"]
        if video.inicio:
            comando += ["-ss", f"{video.inicio:.3f}"]
        comando += ["-i", str(fonte)]
        if video.duracao is not None:
            comando += ["-t", f"{video.duracao:.3f}"]
        comando += ["-vf", FILTRO_ESCALA, *args]

        temporario = destino.with_suffix(".tmp" + destino.suffix)
        resultado = subprocess.run(
            comando + [str(temporario)], capture_output=True, text=True
        )
        if resultado.returncode != 0 or not temporario.exists():
            temporario.unlink(missing_ok=True)
            raise ErroVideoExterno((resultado.stderr or "ffmpeg falhou").strip()[:200])

        temporario.replace(destino)
        return destino

    # -- API ---------------------------------------------------------------

    def obter_par(self, video):
        """Devolve (mp4, webm) do clipe, ou (None, None) se não deu.

        Nada é abortado: a falha fica registrada e o card volta a ser o que era
        sem o link — com o vídeo do INES, se houver, ou com o aviso de lacuna.
        """
        config.CACHE_VIDEOS.mkdir(parents=True, exist_ok=True)
        mp4 = config.CACHE_VIDEOS / f"yt-{video.chave}.mp4"
        webm = config.CACHE_VIDEOS / f"yt-{video.chave}.webm"

        if mp4.exists() and webm.exists() and mp4.stat().st_size > 0:
            self.do_cache += 1
            self._conferir_duracao(video, mp4)
            return mp4, webm

        try:
            fonte = self._fonte(video.url)
            self._cortar(fonte, video, webm, midia.ARGS_VP9)
            self._cortar(fonte, video, mp4, midia.ARGS_H264)
        except ErroVideoExterno as erro:
            self.falhas[video.rotulo] = str(erro)
            return None, None

        self.clipes += 1
        self._conferir_duracao(video, mp4)
        return mp4, webm

    def _conferir_duracao(self, video, clipe):
        """Avisa quando o clipe pronto ficou longo demais para ser um sinal.

        Medido no arquivo, não no `@yt`: um link sem intervalo pode ser um vídeo
        de dez minutos entrando inteiro por esquecimento, ou pode ser um clipe de
        quatro segundos que já é só o sinal. Só o arquivo pronto sabe qual dos
        dois.
        """
        duracao = video.duracao
        if duracao is None:
            duracao = duracao_de(clipe)
        if duracao is not None and duracao > SEGUNDOS_SUSPEITOS:
            self.longos.append(f"{video.rotulo} ({duracao:.0f}s)")

    def resumo(self):
        return {
            "clipes": self.clipes,
            "do_cache": self.do_cache,
            "fontes_baixadas": self.fontes_baixadas,
            "falhas": dict(self.falhas),
            "longos": list(self.longos),
        }
