import signal
from time import sleep

import buttonshim
from inky import InkyWHAT
from picamera import PiCamera
from PIL import Image

camera = PiCamera()

X_RESOLUTION = 1024
Y_RESOLUTION = 768
IMAGE_FILE = 'image.jpg'
X_DISPLAY = 400
Y_DISPLAY = 300
DISPLAY_COLOUR = 'black'

def take_picture():
    """
    Take a picture.
    """
    camera.rotation = 270
    camera.resolution = (1024, 768)
    camera.start_preview()
    sleep(2)
    camera.capture(IMAGE_FILE)


def display_picture():
    """
    Display the picture. Modified from the Pimoroni Inky library dither-image-what.py example.
    """
    inky_display = InkyWHAT(DISPLAY_COLOUR)
    inky_display.set_border(inky_display.WHITE)
    display_image = Image.open(IMAGE_FILE)
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
    take_picture()
    display_picture()


signal.pause()
