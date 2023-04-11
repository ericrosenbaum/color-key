import time
import board
import math
import adafruit_tcs34725
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
sensor = adafruit_tcs34725.TCS34725(i2c)

# Change sensor integration time to values between 2.4 and 614.4 milliseconds
sensor.integration_time = 30
# Change sensor gain to 1, 4, 16, or 60
sensor.gain = 1

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
    (BLACK, (4.0811, -2.127, -5.5206)), # table
    (WHITE, (42.1413, -1.7207, -21.789)), # paper
    (RED, (3.9501, 9.3176, 1.5597)), # dot sticker
    (RED, (6.1586, 20.0941, 6.7464)), # crayola marker
    (ORANGE, (18.9638, 35.4737, 25.5502)), # dot sticker
    (ORANGE, (7.1279, 20.3982, 9.4602)), # crayola marker
    (YELLOW, (18.1606, -3.3514, 21.4392)), # dot sticker
    (YELLOW, (18.8557, -9.6362, 22.0842)), # crayola marker
    (GREEN, (13.071, -20.2436, 14.3274)), # dot sticker
    (GREEN, (7.622, -10.9581, 2.4023)), # LEGO
    (GREEN, (10.5382, -16.8222, 7.805)), # crayola marker
    (BLUE, (4.6772, 6.9863, -22.3077)), # dot sticker
    (BLUE, (5.2427, 11.1113, -27.3197)), # crayola marker
    (PINK, (8.5591, 24.1974, 6.9332)), # dot sticker
    (PINK, (3.4442, 9.3842, -22.7482)), # crayola marker (purple)
]

# https://stackoverflow.com/a/16020102
def rgb2lab ( inputColor ) :

   num = 0
   RGB = [0, 0, 0]

   for value in inputColor :
       value = float(value) / 255

       if value > 0.04045 :
           value = ( ( value + 0.055 ) / 1.055 ) ** 2.4
       else :
           value = value / 12.92

       RGB[num] = value * 100
       num = num + 1

   XYZ = [0, 0, 0,]

   X = RGB [0] * 0.4124 + RGB [1] * 0.3576 + RGB [2] * 0.1805
   Y = RGB [0] * 0.2126 + RGB [1] * 0.7152 + RGB [2] * 0.0722
   Z = RGB [0] * 0.0193 + RGB [1] * 0.1192 + RGB [2] * 0.9505
   XYZ[ 0 ] = round( X, 4 )
   XYZ[ 1 ] = round( Y, 4 )
   XYZ[ 2 ] = round( Z, 4 )

   XYZ[ 0 ] = float( XYZ[ 0 ] ) / 95.047         # ref_X =  95.047   Observer= 2°, Illuminant= D65
   XYZ[ 1 ] = float( XYZ[ 1 ] ) / 100.0          # ref_Y = 100.000
   XYZ[ 2 ] = float( XYZ[ 2 ] ) / 108.883        # ref_Z = 108.883

   num = 0
   for value in XYZ :

       if value > 0.008856 :
           value = value ** ( 0.3333333333333333 )
       else :
           value = ( 7.787 * value ) + ( 16 / 116 )

       XYZ[num] = value
       num = num + 1

   Lab = [0, 0, 0]

   L = ( 116 * XYZ[ 1 ] ) - 16
   a = 500 * ( XYZ[ 0 ] - XYZ[ 1 ] )
   b = 200 * ( XYZ[ 1 ] - XYZ[ 2 ] )

   Lab [ 0 ] = round( L, 4 )
   Lab [ 1 ] = round( a, 4 )
   Lab [ 2 ] = round( b, 4 )

   return Lab

def bar_graph(read_value):
    scaled = int(read_value / 1000)
    return "[%5d] " % read_value + (scaled * "*")

def color_distance(input, target):
    sum = 0
    for i in range(3):
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
#         t = time.monotonic()
        sensor.led = True
        sensor_channels = rgb2lab(sensor.color_rgb_bytes)
        distances = []
        for color, value in values:
            distances.append(color_distance(sensor_channels, value))
        closestIndex = distances.index(min(distances))
        closestColor, v = values[closestIndex]
#         print(time.monotonic() - t)
        print(sensor_channels)

        if closestColor == WHITE or closestColor == BLACK:
#             if a key is down release it
            if key_down != None:
                release(key_down)
        else:
#             if no key is down, press a key
            if key_down == None:
                press(closestColor)
            else:
#                 if a key is down, but we see a different color, release and press the new key
                if key_down != closestColor.key:
                    keyboard.release(key_down)
                    press(closestColor)

