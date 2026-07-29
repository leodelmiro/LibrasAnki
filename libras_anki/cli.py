"""Linha de comando: lê listas de estudo e escreve o .apkg.

    .venv/Scripts/python.exe -m libras_anki
    .venv/Scripts/python.exe -m libras_anki listas/numeros.txt -o out/numeros.apkg
"""

import argparse
import sys

from . import config, gerador, indice, ines, listas, numeros


def _argumentos(argv):
    parser = argparse.ArgumentParser(
        prog="libras_anki",
        description="Gera um baralho Anki de LIBRAS a partir do dicionário do INES.",
    )
    parser.add_argument(
        "listas", nargs="*", type=str,
        help="arquivos de lista (padrão: todos os .txt em listas/)",
    )
    parser.add_argument(
        "-o", "--saida", default=None,
        help="caminho do .apkg (padrão: out/libras.apkg)",
    )
    parser.add_argument(
        "--baralho", default="LIBRAS",
        help="nome do baralho dentro do Anki (padrão: LIBRAS)",
    )
    parser.add_argument(
        "--sem-ordinais", action="store_true",
        help="não gerar os cards de ordinal pendentes de vídeo",
    )
    parser.add_argument(
        "--atualizar-dicionario", action="store_true",
        help="baixar o dicionário de novo em vez de usar o cache",
    )
    return parser.parse_args(argv)


def main(argv=None):
    args = _argumentos(argv if argv is not None else sys.argv[1:])
    config.criar_diretorios()

    if args.atualizar_dicionario:
        print("baixando o dicionário do INES...")
        ines.obter_verbetes(forcar=True)
        ines.obter_tabelas(forcar=True)

    caminhos = [config.RAIZ / p for p in args.listas] or sorted(config.LISTAS.glob("*.txt"))
    caminhos = [p for p in caminhos if p.exists()]
    if not caminhos:
        print("nenhuma lista encontrada em listas/ — crie um arquivo .txt lá.")
        return 1

    print("listas:", ", ".join(p.name for p in caminhos))

    try:
        motor = gerador.Gerador(nome_baralho=args.baralho)
    except ines.FormatoInesMudou as erro:
        print(f"erro: {erro}")
        return 1

    itens = listas.ler_muitas(caminhos, indice.Indice(motor.verbetes))
    motor.adicionar(itens)

    tem_numero = any(numeros.no_escopo(i.texto) for i in itens)
    if tem_numero and not args.sem_ordinais:
        motor._notas_ordinais()

    destino = config.RAIZ / args.saida if args.saida else config.SAIDA / "libras.apkg"
    destino.parent.mkdir(parents=True, exist_ok=True)
    motor.escrever(destino)

    print()
    print(motor.relatorio.texto())
    print(f"\ngerado: {destino}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
