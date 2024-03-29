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

X_RESOLUTION = 768
Y_RESOLUTION = 1024
IMAGES_DIR = os.getenv('IMAGES_DIR')
HEIGHT = 400
WIDTH = 300
DISPLAY_COLOUR = 'black'
S3_BUCKET = os.getenv('S3_BUCKET')
S3_FOLDER = os.getenv('S3_FOLDER')


def take_picture():
    """
    Take a picture.
    """
    camera.resolution = (X_RESOLUTION, Y_RESOLUTION)
    camera.start_preview()
    sleep(2)
    os.makedirs(IMAGES_DIR, exist_ok=True)
    filename = f'{uuid.uuid4()}.png'
    camera.capture(f'{IMAGES_DIR}/{filename}', resize=(WIDTH, HEIGHT))

    return filename


def get_s3_client():
    """
    Get the S3 client.
    """
    return boto3.client(
        's3',
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


def get_rekognition_client():
    """
    Get the Rekognition client.
    """
    return boto3.client(
        'rekognition',
    )


def get_labels(filename):
    """
    Get Rekognition labels.
    """
    client = get_rekognition_client()
    labels = client.detect_labels(
        Image={
            'S3Object': {
                'Bucket': S3_BUCKET,
                'Name': f'{S3_FOLDER}/{filename}',
            },
        },
        MaxLabels=30,
        MinConfidence=70,
    )
    return labels


def get_faces(filename):
    """
    Get Rekognition faces.
    """
    client = get_rekognition_client()
    faces = client.detect_faces(
        Image={
            'S3Object': {
                'Bucket': S3_BUCKET,
                'Name': f'{S3_FOLDER}/{filename}',
            },
        },
        Attributes=[
            'ALL',
        ]
    )
    return faces


def display_picture(filename):
    """
    Display the picture. Modified from the Pimoroni Inky library dither-image-what.py example.
    """
    inky_display = InkyWHAT(DISPLAY_COLOUR)
    inky_display.set_border(inky_display.WHITE)
    display_image = Image.open(f'{IMAGES_DIR}/{filename}')
    display_image = display_image.transpose(Image.ROTATE_90)
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
    labels = get_labels(filename)
    print(labels)
    faces = get_faces(filename)
    print(faces)


signal.pause()
