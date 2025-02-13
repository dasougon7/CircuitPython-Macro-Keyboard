"""CircuitPython HID Macro Keyboard"""
import time

import board
import digitalio
import usb_hid
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode
# Import de ConsumerControl para manejar teclas multimedia
from adafruit_hid.consumer_control import ConsumerControl
from adafruit_hid.consumer_control_code import ConsumerControlCode
# Import para LCD
from adafruit_character_lcd import character_lcd
# Import para Joystick
from analogio import AnalogIn
# Imports para neopixel
import neopixel
from rainbowio import colorwheel

#Imports de clases del proyecto
#from button_matrix import 

#TODO Crear clase Teclado: Definición de pines, matriz teclas, etc.

#TODO Clase LED: pines, funciones, inicialización, funciones_aux, manejo multithread

#TODO Clase Joystick: pines, inicialización, funciones, calibración, manejar modos de uso

#TODO Clase LCD: pines, etc, función inicio, función mostrar combinación, función display de modos

#TODO Archivo principal con secuencia de inicio, inicializaciones, etc

#Declaración de los pines usados para matriz de teclas
#las filas estarán configuradas como pull-ups
row_pins = [board.IO7, board.IO5, board.IO3]
#las columnas estarán configuradas como outputs. Inicializadas a 1 y pasan a 0 cuando se checkean de 1 en una
collum_pins = [board.IO9, board.IO11, board.IO12]

#Pines destinados al uso de LCD

lcd_rs = digitalio.DigitalInOut(board.IO16)
lcd_en = digitalio.DigitalInOut(board.IO18)
lcd_d4 = digitalio.DigitalInOut(board.IO33)
lcd_d5 = digitalio.DigitalInOut(board.IO35)
lcd_d6 = digitalio.DigitalInOut(board.IO37)
lcd_d7 = digitalio.DigitalInOut(board.IO39)


# Matriz de objetos tecla. Objetos pines
row_pin_array = []
collum_pin_array = []

# Inicialización del Objeto Teclado
time.sleep(1)  # Pausa para evitar condición de carrera en algunos sistemas
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # Keyboard Layout. Idk how to make it spanish
consumer_control = ConsumerControl(usb_hid.devices)

# Combinaciones de teclas asignadas a cada botón del teclado.
# Se acompañan con el shift si no son strings
default_macro_set = [
    [(Keycode.ALT, Keycode.TAB), ("Hello World!\n"), (ConsumerControlCode.PLAY_PAUSE, )],
    [(Keycode.B,), (Keycode.C,), (Keycode.D,)],
    [(Keycode.E,), (Keycode.F,), (Keycode.G,)]
    ]

layout = (("Perfil 1",default_macro_set),("Perfil 2", ))
shift_key = Keycode.SHIFT

# Configurar todos los pines de las filas como outputs con valor alto por defecto
for pin in row_pins:
    row_pin = digitalio.DigitalInOut(pin)
    row_pin.direction = digitalio.Direction.OUTPUT
    row_pin.value = True
    row_pin_array.append(row_pin)
    
# Configurar todos los pines de las columnas como inputs con pullups
for pin in collum_pins:
    col_pin = digitalio.DigitalInOut(pin)
    col_pin.direction = digitalio.Direction.INPUT
    col_pin.pull = digitalio.Pull.UP
    collum_pin_array.append(col_pin)


#PRUEBA CLASE MATRIX
#buttons = ButtonMatrix(row_pins, collum_pins)

"""LCD"""
# Configurar LED de la placa para comprobar las pulsaciones
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT

# Inicialización de la clase para pantalla LCD con los pines asignados
# Pantalla 16x2
lcd = character_lcd.Character_LCD(lcd_rs, lcd_en, lcd_d4, lcd_d5,
                                  lcd_d6, lcd_d7, 16, 2)

# Mensaje inicio del teclado
def mensaje_inicio():
    title = "Circuit Python\nMacro Keyboard"
    lcd.message = title
    time.sleep(1)
    
    for i in range(len(title)/2):
        time.sleep(0.5)
        lcd.move_left()
    lcd.clear()

#mensaje_inicio()
# Información del perfil actual
lcd.message = "Hello World!"
lcd.clear()

print("Waiting for key pin...")

"""JOYSTICK"""

def get_voltage(pin):
    return pin.value #* 5) / 65536

joystick_x = AnalogIn(board.IO2)
joystick_y = AnalogIn(board.IO4)

joystick_button = digitalio.DigitalInOut(board.IO38)
joystick_button.direction = digitalio.Direction.INPUT
joystick_button.pull = digitalio.Pull.UP

print(joystick_x.reference_voltage)


"""LEDS"""
leds_pin = board.IO21
leds_size = 9

leds = neopixel.NeoPixel(leds_pin, leds_size, brightness=0.1, auto_write=False)

leds.show()

def color_chase(color, wait):
    for i in range(leds_size):
        leds[i] = color
        time.sleep(wait)
        leds.show()
    time.sleep(0.5)


def rainbow_cycle(wait):
    for j in range(255):
        for i in range(leds_size):
            rc_index = (i * 256 // leds_size) + j
            leds[i] = colorwheel(rc_index & 255)
        leds.show()
        time.sleep(wait)


RED = (255, 0, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
CYAN = (0, 255, 255)
BLUE = (0, 0, 255)
PURPLE = (180, 0, 255)

def rainbow():
    color_chase(RED, 0.1)  # Increase the number to slow down the color chase
    color_chase(YELLOW, 0.1)
    color_chase(GREEN, 0.1)
    color_chase(CYAN, 0.1)
    color_chase(BLUE, 0.1)
    color_chase(PURPLE, 0.1)

    rainbow_cycle(0.01)  # Increase the number to slow down the rainbow
    
f = open("custom_layouts.txt", "r")
print(f.read())

#Bucle de ejecución
while True:
    
    #buttons.check_keypress(keyboard, lcd, leds) PRUEBA CLASE
    #rainbow()
    if not joystick_button.value:
        print("Boton pulsado")
    print(get_voltage(joystick_x), get_voltage(joystick_y))
    
    #Relleno de leds estatico
    #Debería ser personalizable por perfil
    leds.fill(RED)
    leds.show()
    
    n_layout=0
    #if joystick_x >= 12000:
    #    n_layout+=1
        
    lcd.message = layout[n_layout][0]
    #lcd.cursor_position(3,1)
    
    # Checkear cada fila
    for row_pin in row_pin_array:
        i = row_pin_array.index(row_pin)
        # Poniendole valor bajo primero
        row_pin.value = False
        for col_pin in collum_pin_array:
            # Para comprobar a que columna se propaga la señal baja
            if not col_pin.value:
                j = collum_pin_array.index(col_pin)
                print("Key - row: %d " % i)
                print("Key - col: %d \n" %j)
                # Encendemos el LED de la placa con la pulsación del botón
                led.value = True
                
                # Mientras la fila este a 0 y el valor de la columna sea igual
                # Tenemos el botón (i,j) pulsado
                while not row_pin.value and not col_pin.value:
                    #Mientras se pulsa el botón, se ilumina de otro color
                    leds[i*3+j*1] = GREEN
                    leds.show()
                    
                    pass  # Esperamos a que se deje de pulsar la tecla
                # Mandar las combinaciones de teclas o escribir string en su caso
                key = default_macro_set[i][j]  # Acceso a la tupla que guarda la macro
                
                #TODO enseñar en lcd macro usada
                
                if isinstance(key, str):  # Si es una string...
                    keyboard_layout.write(key)  #  ... escribimos el string
                elif len(key)>= 1:
                    if(key[0] == 205): #Prueba del ConsumerControl. 205 es el código de la tecla PLAY/PAUSE
                        consumer_control.press(key[0])
                        time.sleep(0.5)
                        consumer_control.release()
                    for keyy in key:
                        keyboard.press(keyy)
                    keyboard.release_all()
                else:  # Si no lo es
                    keyboard.press(shift_key, key)  # Pulsación de macro (con la tecla shift)...
                    keyboard.release_all()  # ... "Soltamos" la macro

                # Apagamos el LED como fin de la pulsación
                led.value = False
        # Volvemos a poner la fila en alto para comprobar la siguiente
        row_pin.value = True

    time.sleep(0.2)
