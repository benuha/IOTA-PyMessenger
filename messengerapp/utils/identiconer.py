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

import sys
from PyQt5 import QtCore, QtWidgets

from PIL import Image, ImageDraw, ImageOps
from PIL.ImageQt import ImageQt
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QImage, QPixmap, QColor

import logging

from PyQt5.QtWidgets import QApplication, QLabel, QStyle

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


def create_identicon_pil(ident_str, size=420, pixel=70, border=35, background='#EFEFEF'):
    hash_id = get_md5_from(ident_str)
    color = tuple([int(x, 16) for x in (hash_id[0:2], hash_id[2:4], hash_id[4:6])])
    pixels = get_pixels(int(hash_id[6:], 16))
    image = Image.new("RGB", (size, size), background)
    draw = ImageDraw.Draw(image)

    for i in range(5):
        for j in range(5):
            if pixels[i][j] == '1':
                x = j * pixel + border
                y = i * pixel + border
                draw.rectangle(
                    ((x, y), (x + pixel, y + pixel)),
                    fill=color,
                    outline=color)

    mask = Image.new('L', (size, size), 0)
    draw = ImageDraw.Draw(mask)
    draw.ellipse(((0, 0), (0 + size, 0 + size)), fill=255)
    output = ImageOps.fit(image, mask.size, centering=(0, 0))
    output.putalpha(mask)

    return output


if __name__ == '__main__':
    # iden = Identicon("9MKUUEKQRWZOVZBBLLUXGC9EDYWNVCWZLKPDUJEHVCDHCFPFLPZAOJC9QEXWCIL9HOUUWMDCAWGFAFSJM")
    iden = create_identicon_pil("Y9UYQNOKBIOKXTIYPUJKENVQF9KGLLYHVBJJUTFSNFVZOTR9LWDEIVLGYHLDFROBGIKGIIHVRWZRKYZ9Z")

    # mask = Image.new('L', (420, 420), 0)
    # draw = ImageDraw.Draw(mask)
    # draw.ellipse(((0, 0), (0 + 420, 0 + 420)), fill=255)
    # output = ImageOps.fit(iden, mask.size, centering=(0, 0))
    # output.putalpha(mask)
    # output.show()

    # Create a no-brain QtApp with a label and add image to the label
    app = QApplication(sys.argv)
    label = QLabel()
    # label.palette().setColor(label.backgroundRole(), QColor(255, 255, 255))
    label.setMaximumSize(QSize(41, 41))
    # Convert from PIL Image -> QImage -> QPixmap
    # convert PIL image to a PIL.ImageQt object
    imageq = ImageQt(iden)
    # cast PIL.ImageQt object to QImage object -that´s the trick!!!
    qimage = QImage(imageq)
    qpixm = QPixmap(qimage)

    # label.setGeometry(QtCore.QRect(20, 10, 41, 41))
    # label.setAutoFillBackground(True)
    label.setFrameShape(QtWidgets.QFrame.Box)
    label.setText("")
    label.setScaledContents(True)

    label.setPixmap(qpixm)
    label.show()

    sys.exit(app.exec_())
