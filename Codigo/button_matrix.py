"""Esta clase era una prueba para extraer clases del código principal.
    No termina de funcionar hasta la fecha con las pruebas realizadas
    pero dejo el archivo para trabajo futuro
"""

import time

import board
import digitalio
import usb_hid

from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS
from adafruit_hid.keycode import Keycode

class ButtonMatix:
    """ Clase para la matriz de teclas del teclado CPMK
    con constructor y funciones auxiliares para el manejo de las pulsaciones
    """

    def __init__(self, row_pins, collum_pins):
        self.rows = []
        self.collums = []
        
        self.shift_key = Keycode.SHIFT

        self.current_layout = 1

        self.layout_names = {1:"Multimedia", 2:"IDE"}
        self.layout_macros = {1: [
            [Keycode.A, "Hello World!\n", Keycode.V],
            [Keycode.B, Keycode.C, Keycode.D],
            [Keycode.E, Keycode.F, Keycode.G]
        ],
                               2: []}
        self.rows_config(row_pins)
        self.collums_config(collum_pins)

    def rows_config(self, row_pins):
        for pin in row_pins:
            row_pin = digitalio.DigitalInOut(pin)
            row_pin.direction = digitalio.Direction.OUTPUT
            row_pin.value = True
            self.rows.append(row_pin)

    def collums_config(self, collum_pins):
        for pin in collum_pins:
            col_pin = digitalio.DigitalInOut(pin)
            col_pin.direction = digitalio.Direction.INPUT
            col_pin.pull = digitalio.Pull.UP
            self.collums.append(col_pin)
    
    def check_keypress(self, keyboard, lcd, leds):
        for row in self.rows:
            i = self.rows.index(row)
            row.value = False

            for col in self.collums:
                if not col.value:
                    j = self.collums.index(col)
                    # Iluminar aqui led correspondiente
                    while not row.value and not col.value:
                        pass # Esperamos a que se suelte el botón de la macro

                    macros = self.layout_macros.get(self.current_layout) #Cargo las macros del perfil actual
                    key = macros[i][j] #Accedo a la macro pulsada dentro del perfil actual
                    #Iluminara el led correspondiente a la macro ESTO SERÍA EN EL WHILE: PASS
                    leds[i*3+j].setPixelColor()
                    leds.show()
                    #Mostrar en la pantalla el nombre de la macro
                    if self.layout_macro_names:
                        lcd.print_macro(self.layout_macro_names[i][j])
                    """Si key = 1, pulsarla, si no, si key >= 2, pulsar el orden de las teclas"""                    
                    keyboard.press()
            row.value = True

        

