#!/bin/sh

# TODO set config values
cover_src=060-rotate-crop/231.jpg

magick "$cover_src" -scale 50% -quality 50% cover.avif
