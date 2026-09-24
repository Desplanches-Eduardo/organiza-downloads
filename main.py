from pathlib import Path
import shutil

types = {
    "Documentos": ["pdf", "doc", "docx", "xls", "xlsx", "ppt", "pptx", "txt", "csv", "epub"],
    "Imagens":    ["jpg", "jpeg", "png", "gif", "bmp", "svg", "webp", "heic"],
    "Videos":     ["mp4", "mkv", "avi", "mov", "webm"],
    "Audio":      ["mp3", "wav", "flac", "m4a", "ogg"],
    "Compactados":["zip", "rar", "7z", "tar", "gz", "iso"],
    "Codigo":     ["py", "js", "ts", "html", "css", "json", "xml", "yaml", "sh", "ipynb"],
    "Executaveis":["exe", "msi", "deb", "rpm", "apk", "dmg", "appimage"],
    "Fontes":     ["ttf", "otf"],
}

path = Path.home() / "Downloads"


full_list = list(path.iterdir())

for categoria in types:
    (path / categoria).mkdir(parents=True, exist_ok=True)

for item in full_list:
    if not item.is_file():
        continue

    ext = item.suffix.lower().lstrip('.')
    if not ext:
        continue

    for categoria, extensoes in types.items():
        if ext in extensoes:
            new_path = path / categoria / item.name

            if item != new_path:
                shutil.move(item, new_path)
                print(f"Movido: {item.name} -> {categoria}/")
            break
