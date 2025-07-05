"""CircuitPython HID Macro Keyboard"""
# Imports para la configuración de la placa como un teclado
import time
import board
import digitalio
import usb_hid
# Imports para matriz de botones
from adafruit_hid.keyboard import Keyboard
from adafruit_hid.keyboard_layout_us import KeyboardLayoutUS #Necesario para imprimir strings
from adafruit_hid.keycode import Keycode #Necesario para representar teclas individuales
# Imports para LCD
from adafruit_character_lcd import character_lcd


# Inicialización del Objeto Teclado
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # Layout asignado al teclado

# Configurar LED de la placa para comprobar las pulsaciones
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


"""Matriz de botones"""
#Declaración de los pines usados para matriz de teclas
#Las filas estarán configuradas como  outputs. Inicializadas a 1 y pasan a 0 cuando se van recorriendo
#Las columnas estarán configuradas como inputs con resistencias pull-ups
row_pins = [board.IO7, board.IO5]
collum_pins = [board.IO9, board.IO11]

# Matriz de objetos tecla. En estos arrays almacenaremos los pines una vez configurados
row_pin_array = []
collum_pin_array = []

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

# Teclas asignadas a cada botón del teclado. Aquí podemos customizar las macros de cada tecla
default_macro_set = [
    [(Keycode.A,), (Keycode.B,)],
    [(Keycode.ALT, Keycode.TAB), ("Hello! I am CPMK :)")],
    ]

shift_key = Keycode.SHIFT 



"""Pantalla LCD"""
#Pines destinados al uso de LCD
lcd_rs = digitalio.DigitalInOut(board.IO16)
lcd_en = digitalio.DigitalInOut(board.IO18)
lcd_d4 = digitalio.DigitalInOut(board.IO33)
lcd_d5 = digitalio.DigitalInOut(board.IO35)
lcd_d6 = digitalio.DigitalInOut(board.IO37)
lcd_d7 = digitalio.DigitalInOut(board.IO39)

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

mensaje_inicio()


# Bucle de ejecución
while True:
    # Checkear casda fila
    for row_pin in row_pin_array:
        i = row_pin_array.index(row_pin)
        # Poniendole valor bajo primero
        row_pin.value = False
        for col_pin in collum_pin_array:
            # Para comprobar a que columna se propaga la señal baja
            if not col_pin.value:
                j = collum_pin_array.index(col_pin)
                #print("Key - row: %d " % i)
                #print("Key - col: %d \n" %j)
                led.value = True # Encendemos el LED de la placa con la pulsación del botón
                
                # Mientras la fila este a 0 y tengamos una columna con el mismo valor
                # Tenemos el botón (i,j) pulsado
                # Mandamos la combinación de teclas o escribir string en su caso
                macro = default_macro_set[i][j]  # Acceso al array que guarda las macro
                
                if isinstance(macro, str):  # Si es una string...
                    keyboard_layout.write(macro)  #  ... escribimos el string
                elif len(macro)>= 1:  # Si la macro contiene varias 
                    for key in macro:
                        keyboard.press(key)  # ...se pulsan una a una y se sueltan juntas
                    keyboard.release_all()
                else:  # Si solo contiene 1 
                    keyboard.press(shift_key, macro)  # Pulsación de macro (con la tecla shift)...
                    keyboard.release_all()  # ... soltamos la macro
                led.value = False # Apagamos el LED como fin de la pulsación
                
        row_pin.value = True # Volvemos a poner la fila en alto para comprobar la siguiente

    time.sleep(0.2)