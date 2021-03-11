import os
from io import BytesIO
from random import *

from PIL import Image, ImageDraw, ImageFont

TEMPLATE_PATH = "files/ticket.png"
FONT_PATH = "files/Roboto-Regular.ttf"
FONT_SIZE = 16

BLACK = (0, 0, 0, 255)

AVATAR_OFFSET = (10, 10)


def generate_ticket(departure, arrival, date, quantity, number):
    base = Image.open(TEMPLATE_PATH)
    font = ImageFont.truetype(FONT_PATH, FONT_SIZE)
    d = ImageDraw.Draw(base)
    d.text((100, 280), departure, font=font, fill=BLACK)
    d.text((100, 331), arrival, font=font, fill=BLACK)
    d.text((65, 382), date, font=font, fill=BLACK)
    d.text((270, 434), quantity, font=font, fill=BLACK)
    d.text((188, 484), number, font=font, fill=BLACK)

    path = 'files/avatars'
    random_image = choice(os.listdir(path))
    avatar = Image.open(path + '/' + random_image)
    base.paste(avatar, (330, 290))

    temp_file = BytesIO()
    base.save(temp_file, 'png')
    temp_file.seek(0)

    return temp_file
