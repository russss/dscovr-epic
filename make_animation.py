# coding=utf-8
from __future__ import division, absolute_import, print_function, unicode_literals
import tempfile
from datetime import date
from epic import EPIC
from processing import process_image

e = EPIC()

i = 0
for image in e.get_image_range(date(2015, 10, 13), date(2015, 10, 21)):
    with tempfile.NamedTemporaryFile(suffix='.png') as downloadfile:
        e.download_image(image['image'], downloadfile)
        process_image(downloadfile.name, "./out/img%03d.png" % i)
    i += 1

# avconv -f image2 -r 30 -i ./img%03d.png -s 1024x1024 ./output.mp4
