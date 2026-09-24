"""Organiza ~/Downloads por tipo de arquivo.

Agendado pelo cron (ver `crontab -l`). Só biblioteca padrão.
"""

from __future__ import annotations

import shutil
import time
from datetime import datetime
from pathlib import Path

DOWNLOAD_DIR = Path.home() / "Downloads"

# extensão -> pasta de destino
types = {
    "Documentos":  ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "epub"],
    "Imagens":     ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "heic"],
    "Videos":      ["mp4", "mkv", "avi", "mov", "webm"],
    "Audio":       ["mp3", "wav", "flac", "m4a", "ogg"],
    "Compactados": ["zip", "rar", "7z", "tar", "gz", "iso"],
    "Codigo":      ["py", "js", "ts", "html", "css", "json", "xml", "yaml", "sh", "ipynb"],
    "Executaveis": ["exe", "msi", "deb", "rpm", "apk", "dmg", "appimage"],
    "Fontes":      ["ttf", "otf"],
}

CATEGORIA_DA_EXTENSAO = {
    extensao: categoria
    for categoria, extensoes in types.items()
    for extensao in extensoes
}

# quanto tempo esperar antes de mexer num arquivo: abaixo disso ele ainda
# pode estar sendo escrito pelo navegador
MIN_IDADE_SEGUNDOS = 3 * 60

SUFIXOS_INCOMPLETOS = {
    ".crdownload",  # Chrome
    ".part",        # Firefox, wget -c
    ".partial",     # Edge
    ".download",    # Safari
    ".filepart",    # Falkon
    ".opdownload",  # Opera
    ".tmp",
    ".temp",
}

MAX_TENTATIVAS_NOME = 1_000  # trava contra loop infinito


def deve_ignorar(arquivo: Path, agora: float) -> bool:
    nome = arquivo.name

    # ocultos, e as travas do Office (~$relatorio.docx)
    if nome.startswith(".") or nome.startswith("~$"):
        return True

    if arquivo.suffix.lower() in SUFIXOS_INCOMPLETOS:
        return True

    try:
        modificado_em = arquivo.stat().st_mtime
    except OSError:
        # foi cancelado/removido no meio do caminho
        return True

    return (agora - modificado_em) < MIN_IDADE_SEGUNDOS


def destino_livre(destino: Path) -> tuple[Path, bool]:
    """Vira "nome (1).ext" se já houver algo no caminho. O bool avisa se renomeou."""
    if not destino.exists():
        return destino, False

    for contador in range(1, MAX_TENTATIVAS_NOME + 1):
        candidato = destino.with_name(f"{destino.stem} ({contador}){destino.suffix}")
        if not candidato.exists():
            return candidato, True

    raise RuntimeError(f"Nenhum nome livre para {destino.name}")


def organizar(pasta: Path) -> None:
    if not pasta.is_dir():
        print(f"Pasta não encontrada, nada a fazer: {pasta}")
        return

    agora = time.time()
    itens = [item for item in pasta.iterdir() if item.is_file()]

    movidos = renomeados = ignorados = falhas = 0

    for item in itens:
        if deve_ignorar(item, agora):
            ignorados += 1
            continue

        categoria = CATEGORIA_DA_EXTENSAO.get(item.suffix.lower().lstrip("."))
        if categoria is None:
            continue  # extensão fora da lista

        destino, colidiu = destino_livre(pasta / categoria / item.name)
        destino.parent.mkdir(parents=True, exist_ok=True)

        try:
            shutil.move(str(item), str(destino))
        except OSError as erro:
            falhas += 1
            print(f"FALHA: {item.name} -> {categoria}/ ({erro})")
            continue

        movidos += 1
        if colidiu:
            renomeados += 1
            print(f"Movido: {item.name} -> {categoria}/{destino.name}   (já existia, renomeado)")
        else:
            print(f"Movido: {item.name} -> {categoria}/")

    # uma linha por execução: log parado = cron morto
    print(
        f"[{datetime.now():%Y-%m-%d %H:%M}] {movidos} movido(s), "
        f"{renomeados} renomeado(s), {ignorados} ignorado(s), {falhas} falha(s)."
    )


def main() -> None:
    organizar(DOWNLOAD_DIR)


if __name__ == "__main__":
    main()
