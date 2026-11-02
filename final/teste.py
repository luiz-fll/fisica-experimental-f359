"""Ponto de entrada estrutural; a análise será implementada em seguida."""
import argparse
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Analisa cada filmagem do pássaro bebedor isoladamente."
    )
    parser.add_argument("--diretorio", type=Path, default=Path("dados"),
                        help="Pasta com uma subpasta por filmagem")
    parser.add_argument("--saida", type=Path, default=Path("resultados"),
                        help="Pasta de saída")
    parser.add_argument("--janela", type=float, default=200,
                        help="Duração das janelas em segundos (padrão: 200)")
    args = parser.parse_args()
    if not args.diretorio.is_dir():
        parser.error(f"A pasta de dados não existe: {args.diretorio}")
    if args.janela <= 0:
        parser.error("--janela precisa ser maior que zero.")
    filmagens = sorted(p for p in args.diretorio.iterdir() if p.is_dir())
    if not filmagens:
        parser.error(f"Nenhuma subpasta de filmagem encontrada em: {args.diretorio}")
    print("Estrutura reconhecida; a análise ainda não foi implementada.")
    print(f"Filmagens encontradas: {len(filmagens)}")
    for pasta in filmagens:
        print(f" - {pasta.name}")
    print(f"Saída prevista: {args.saida}")
    print(f"Janela: {args.janela:g} s")

if __name__ == "__main__":
    main()
