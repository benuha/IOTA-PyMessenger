"""
A class to generate identicon image as human brain is faster at telling images apart
than it is at finding differences in written hash string

This's a fork from project:
# Project   Identicon Generator
# Author    Barnabas Markus
# Email     barnabasmarkus@gmail.com
# Date      11.11.2017
# Python    3.6.0
# License   MIT
# Link      https://github.com/BarnabasMarkus/identicon
"""

import hashlib

from PIL import Image, ImageDraw, ImageOps
from PIL.ImageQt import ImageQt
from PyQt5.QtGui import QImage

import logging

logger = logging.getLogger(__name__)


def get_pixels(custom_int):
    chunk = lambda xs, size: [xs[s:s + size] for s in range(0, len(xs), size)]
    extend = lambda xs: xs + xs[0:5] + xs[5:10]
    rotate = lambda xxs: [[xs[i] for xs in xxs] for i in range(5)]

    value = custom_int % (2 ** 15)
    bits = '{:015b}'.format(value)
    pixels = rotate(extend(chunk(bits, 5)))
    return pixels


def get_md5_from(text):
    hash = hashlib.md5()
    hash.update(text.encode('utf-8'))
    return hash.hexdigest()


class Identicon(object):

    def __init__(self, ident_str):
        self.hash_id = get_md5_from(ident_str)
        logger.info("Init identicon for str: {}".format(self.hash_id))
        # using the first six hexadecimal num to decide the color
        self.color = tuple([int(x, 16) for x in (self.hash_id[0:2], self.hash_id[2:4], self.hash_id[4:6])])
        self.pixels = get_pixels(int(self.hash_id[6:], 16))
        self.image = None
        self._draw(size=480)

    def _draw(self, pixel=70, border=35, size=420, background='#EFEFEF'):
        self.image = Image.new("RGB", (size, size), background)
        draw = ImageDraw.Draw(self.image)

        for i in range(5):
            for j in range(5):
                if self.pixels[i][j] == '1':
                    x = j * pixel + border
                    y = i * pixel + border
                    draw.rectangle(
                        ((x, y), (x + pixel, y + pixel)),
                        fill=self.color,
                        outline=self.color)

    def show(self):
        self.image.show()

    def save(self, extension='.jpg'):
        fname = str(self.hash_id) + extension
        self.image.save(fname, "JPEG")

    def convert_pil_to_qimage(self):
        """converts a PIL image to QImage"""
        # convert PIL image to a PIL.ImageQt object
        imageq = ImageQt(self.image)
        # cast PIL.ImageQt object to QImage object -that´s the trick!!!
        qimage = QImage(imageq)
        return qimage


if __name__ == '__main__':
   # iden = Identicon("9MKUUEKQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLPZAOJC9QEXWCIL9HOUUWMDCAWGFAFSJM")
   iden = Identicon("Y9UYQNOKBIOKXTIYPUJKENVQF9KGLLYHVBJJUTFSNFVZOTR9LWDEIVLGYHLDFROBGIKGIIHVRWZRKYZ9Z")

   mask = Image.new('L', (420, 420), 0)
   draw = ImageDraw.Draw(mask)
   draw.ellipse(((0, 0), (0 + 420, 0 + 420)), fill=255)
   output = ImageOps.fit(iden.image, mask.size, centering=(0, 0))
   output.putalpha(mask)
   output.show()
