#!/usr/bin/env python3

import glob
import os
import re
import shutil
import subprocess
import sys
import zipfile
from datetime import datetime
from pathlib import Path

from _shared import (
    load_config,
    get_page_num,
)


src = Path("090-ocr")

# write EPUB file
# dst = Path(Path(__file__).stem + ".epub")

# write unpacked EPUB files to workdir
dst = Path(".")


config = load_config()


if dst != Path(".") and dst.exists():
    print(f"error: output exists: {dst}")
    sys.exit(1)


# downscale to 300 dpi
# 600 dpi -> 300 dpi: 90 MB -> 60 MB
scale = 300 / config.scan_resolution


hocr_to_epub_fxl = "hocr-to-epub-fxl"

args = [
    hocr_to_epub_fxl,
    "--output", str(dst),
]

if dst == Path("."):
    args.append("--output-unpacked")


def git_modified():
    return subprocess.check_output(
        ["git", "show", "-s", "--format=%cI", "HEAD"],
        text=True,
    ).strip()


def stat_modified(path):
    ts = Path(path).stat().st_mtime
    dt = datetime.fromtimestamp(ts).astimezone()
    return dt.isoformat(timespec="seconds")


doc_modified = max(
    git_modified(),
    stat_modified(src),
)


args += [
    "--scale", str(scale),
    "--image-format", "avif",
    "--text-format", "html",
    # TODO? move these config items to 000-config.py
    "--doc-modified", doc_modified,
    "--doc-title", "Tatort Vergangenheit",
    "--doc-subtitle", "Wie eine Fake Past unsere Zukunft diktiert",
    "--doc-description", """Es muss kein Blut geflossen sein, damit Vergangenheit zum Tatort wird. Die Täter benutzten Tinte und Feder, um Geschichten und Personen in die Welt zu setzen. Wir sind die Opfer, wenn uns Schulbücher und Geschichtswerke vorgaukeln, die Vergangenheit zu kennen. Lügen, die wir glauben, verwandeln sich in „Wahrheiten“, mit denen wir leben. Viele Zeugnisse unserer Vergangenheit fehlen, tauchten unvermutet auf und verschwanden wieder. Unsere Geschichte ist ein Labyrinth von Kopien fraglicher Herkunft. Eine Exkursion in den Irrgarten der Geschichten, die zur Geschichte geworden sind. Unsere Zukunft ist in Nebel gehüllt. Wer jedoch weiß, wie unsere Vergangenheit manipuliert wurde, kann daraus ableiten, was kommt.

Dr. med. Gerd Reuther ist Radiologe, Medizinhistoriker und der meistgelesene Medizinaufklärer im deutschsprachigen Raum. Er hat 9 Bücher veröffentlicht. Darunter „Hauptsache Panik. Ein neuer Blick auf Pandemien in Europa“, „Die Eroberung der Alten und Neuen Welt. Mythen und Fakten“ und „Hauptsache krank?“ 

Mit 17 farbigen und 2 schwarzweißen Illustrationen.

Das neue Buch von Gerd Reuther „Tatort Vergangenheit. Wie eine Fake Past unsere Zukunft diktiert“ nimmt sich dieses Themas an und fördert Erschütterndes zutage. Es geht dabei nicht vorrangig um die medizinische Vergangenheit, die der Autor schon öfter entzaubert hat. Dieses Mal hat er sich die „große“ Geschichte vorgenommen: die Antike, Karl den Großen und die Renaissance.
Jochen Sommer bei ansage.org""",
    "--doc-subject", "",
    "--doc-date", "2025",
    "--doc-edition", "1",
    "--doc-extent", "230 pages",
    "--doc-author", "Gerd Reuther",
    # "--doc-introducer", "",
    # "--doc-contributor", "",
    # "--doc-translator", "",
    "--doc-publisher", "Engelsdorfer Verlag, Leipzig",
    "--doc-language", "de",
    "--doc-isbn", "9783690950039",
    "--doc-cover-image", "070-deskew/231.jpg",
    "--canonical-url-base", "https://milahu.github.io/gerd-reuther-tatort-vergangenheit-2025/",
]


print(">", shlex.join(args + sys.argv[1:]) + f" {src}/*.hocr")


hocr_files = src.glob("*.hocr")

subprocess.run(
    args + sys.argv[1:] + hocr_files,
    check=True,
)


if dst == Path("."):
    print("done ./index.xhtml")
    sys.exit(0)


print(f"done {dst}")


# extract the EPUB content files

# rm -rf $dst.unzip
unzip_dir = Path(str(dst) + ".unzip")
shutil.rmtree(unzip_dir, ignore_errors=True)
unzip_dir.mkdir()


# unzip -q ../$dst
with zipfile.ZipFile(dst) as z:
    z.extractall(unzip_dir)


print(f"done {unzip_dir}/index.html")
