import os
import signal
import uuid
from time import sleep

import boto3
import buttonshim
from inky import InkyWHAT
from picamera import PiCamera
from PIL import Image

camera = PiCamera()

X_RESOLUTION = 1024
Y_RESOLUTION = 768
IMAGES_DIR = os.getenv('IMAGES_DIR')
X_DISPLAY = 400
Y_DISPLAY = 300
DISPLAY_COLOUR = 'black'
AWS_ACCESS_KEY_ID = os.getenv('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.getenv('AWS_SECRET_ACCESS_KEY')
S3_BUCKET = os.getenv('S3_BUCKET')
S3_FOLDER = os.getenv('S3_FOLDER')


def take_picture():
    """
    Take a picture.
    """
    camera.rotation = 270
    camera.resolution = (1024, 768)
    camera.start_preview()
    sleep(2)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    filename = f'{uuid.uuid4()}.png'
    camera.capture(f'{IMAGES_DIR}/{filename}')

    return filename


def get_s3_client():
    """
    Get the S3 client.
    """
    return boto3.client(
        's3',
        aws_access_key_id=AWS_ACCESS_KEY_ID,
        aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    )


def save_image_to_s3(filename):
    """
    Save image to S3.
    """
    client = get_s3_client()
    client.upload_file(
        f'{IMAGES_DIR}/{filename}',
        S3_BUCKET,
        f'{S3_FOLDER}/{filename}',
    )


def display_picture(filename):
    """
    Display the picture. Modified from the Pimoroni Inky library dither-image-what.py example.
    """
    inky_display = InkyWHAT(DISPLAY_COLOUR)
    inky_display.set_border(inky_display.WHITE)
    display_image = Image.open(f'{IMAGES_DIR}/{filename}')
    width, height = display_image.size
    height_new = Y_DISPLAY
    width_new = int((float(width) / height) * height_new)
    width_cropped = X_DISPLAY
    display_image = display_image.resize((width_new, height_new), resample=Image.LANCZOS)
    x0 = (width_new - width_cropped) / 2
    x1 = x0 + width_cropped
    y0 = 0
    y1 = height_new
    display_image = display_image.crop((x0, y0, x1, y1))
    palette_image = Image.new('P', (1, 1))
    palette_image.putpalette((255, 255, 255, 0, 0, 0, 255, 0, 0) + (0, 0, 0) * 252)
    display_image = display_image.convert('RGB').quantize(palette=palette_image)
    inky_display.set_image(display_image)
    inky_display.show()


@buttonshim.on_press(buttonshim.BUTTON_A)
def take_and_display_picture(button, pressed):
    """
    Takes a picture and displays it on the Inky wHAT screen.
    """
    filename = take_picture()
    save_image_to_s3(filename)
    display_picture(filename)


signal.pause()
