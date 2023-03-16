import time
import board
import math
from adafruit_as7341 import AS7341
from adafruit_as7341 import Gain
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keycode import Keycode
import digitalio
import neopixel

pixel = neopixel.NeoPixel(board.NEOPIXEL, 1)
pixel.brightness = 0.3

button = digitalio.DigitalInOut(board.A1)
button.switch_to_input(pull=digitalio.Pull.UP)

i2c = board.I2C()  # uses board.SCL and board.SDA
sensor = AS7341(i2c)

keyboard = Keyboard(usb_hid.devices)
key_down = None

class ColorKey:
    values = []
    rgb = (0,0,0)
    key = ''

WHITE = ColorKey()
WHITE.rgb = None
WHITE.key = None

BLACK = ColorKey()
BLACK.rgb = None
BLACK.key = None

RED = ColorKey()
RED.rgb = (255,0,0)
RED.key = Keycode.LEFT_ARROW

ORANGE = ColorKey()
ORANGE.rgb = (255,80,0)
ORANGE.key = Keycode.RIGHT_ARROW

YELLOW = ColorKey()
YELLOW.rgb = (255,255,0)
YELLOW.key = Keycode.UP_ARROW

GREEN = ColorKey()
GREEN.rgb = (0,255,0)
GREEN.key = Keycode.DOWN_ARROW

BLUE = ColorKey()
BLUE.rgb = (0,0,255)
BLUE.key = Keycode.SPACE

PINK = ColorKey()
PINK.rgb = (255,0,255)
PINK.key = Keycode.W

values = [
    (WHITE, (59, 464, 371, 547, 549, 568, 558, 382)), #paper
    (BLACK, (5, 38, 31, 48, 51, 51, 48, 32)), # table
    (RED, (17, 77, 69, 76, 88, 213, 389, 263)), # LEGO
    (RED, (25, 120, 106, 128, 125, 294, 516, 364)), # dot sticker
    (ORANGE, (40, 108, 133, 198, 313, 876, 818, 473)), # dot sticker
    (ORANGE, (22, 61, 107, 178, 212, 362, 421, 289)), # specdrum
    (YELLOW, (33, 96, 128, 322, 472, 539, 530, 341)), # LEGO
    (YELLOW, (38, 106, 135, 440, 547, 585, 580, 393)), # dot sticker
    (GREEN, (11, 73, 99, 200, 134, 76, 69, 47)), # LEGO
    (GREEN, (23, 85, 153, 506, 401, 233, 168, 137)), # dot sticker
    (BLUE, (18, 220, 176, 157, 99, 78, 84, 61)),
    (PINK, (38, 232, 152, 113, 156, 567, 691, 420))
]

sensor.led_current = 5
sensor.led = False

# sensor.gain = 0.5
# sensor.gain = Gain.GAIN_0_5X
# sensor.gain = Gain.GAIN_512X

sensor.atime = 1

# time to read all channels
# default atime 100 astep 999
# default settings: 0.625
# atime 10: 0.12

def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

def color_distance(input, target):
    sum = 0
    for i in range(8):
        sum += (target[i] - input[i])**2
    return math.sqrt(sum)

def press(colorKey):
    global keys, rgb_colors, key_down, keyboard, pixel
    key_down = colorKey.key
    keyboard.press(colorKey.key)
    pixel.fill(colorKey.rgb)

def release(key):
    global keyboard, key_down, pixel
    keyboard.release(key)
    key_down = None
    pixel.fill((0,0,0))

while True:
    pressed = not button.value
    if not pressed:
        sensor.led = False
        if key_down != None:
            release(key_down)
    else:
        t = time.monotonic()
        sensor.led = True
        sensor_channels = sensor.all_channels
        print(sensor_channels)
        distances = []
        for color, value in values:
            distances.append(color_distance(sensor_channels, value))
        closestIndex = distances.index(min(distances))
        closestColor, v = values[closestIndex]
        print(time.monotonic() - t)

        if closestColor == WHITE or closestColor == BLACK:
            # if a key is down release it
            if key_down != None:
                release(key_down)
        else:
            # if no key is down, press a key
            if key_down == None:
                press(closestColor)
            else:
                # if a key is down, but we see a different color, release and press the new key
                if key_down != closestColor.key:
                    keyboard.release(key_down)
                    press(closestColor)

