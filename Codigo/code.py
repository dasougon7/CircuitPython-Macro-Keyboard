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
from adafruit_hid.consumer_control import ConsumerControl # Import de ConsumerControl para manejar teclas multimedia
from adafruit_hid.consumer_control_code import ConsumerControlCode
from adafruit_hid.mouse import Mouse

# Import para LCD
from adafruit_character_lcd import character_lcd

# Import para Joystick
from analogio import AnalogIn

# Imports para neopixel
import neopixel
from rainbowio import colorwheel


# Inicialización del Objeto Teclado
keyboard = Keyboard(usb_hid.devices)
keyboard_layout = KeyboardLayoutUS(keyboard)  # Layout asignado al teclado
consumer_control = ConsumerControl(usb_hid.devices) # Inicializamos el ConsumerControl para teclas multimedia
mouse = Mouse(usb_hid.devices)

# Configurar LED de la placa para comprobar las pulsaciones
led = digitalio.DigitalInOut(board.LED)
led.direction = digitalio.Direction.OUTPUT


"""Matriz de botones"""
#Declaración de los pines usados para matriz de teclas
#Las filas estarán configuradas como  outputs. Inicializadas a 1 y pasan a 0 cuando se van recorriendo
#Las columnas estarán configuradas como inputs con resistencias pull-ups
row_pins = [board.IO7, board.IO5, board.IO3]
collum_pins = [board.IO9, board.IO11, board.IO12]

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
def mensaje_inicio(tiempo_leds, ruta_perfiles):
    title = "Circuit Python\nMacro Keyboard"
    lcd.message = title
    time.sleep(1)
    
    nuevos_layouts = cargar_layouts_personalizados(ruta_perfiles)
    
    for i in range(len(title)/2):
        rainbow_cycle(tiempo_leds)
#         time.sleep(0.3)
        lcd.move_left()
    lcd.clear()
    
    return nuevos_layouts
    
def mostrar_macro(nombre_macro):
    lcd.cursor_position(0,2)
    lcd.message = nombre_macro
    
    

"""JOYSTICK"""
# Función para leer la señal analy
def get_voltage(pin):
    return (pin.value * 3.3) / 65536

# Inicialización de las entradas del joystick
joystick_x = AnalogIn(board.IO2)
joystick_y = AnalogIn(board.IO4)

joystick_button = digitalio.DigitalInOut(board.IO38)
joystick_button.direction = digitalio.Direction.INPUT
joystick_button.pull = digitalio.Pull.UP

# Thresholds para manejas las entradas analógicas del joystick. Como tengo poca resolución por la zona
# de voltaje alto, el threshold superior es prácticamente el valor maximo que podemos leer
joystick_upper_threshold = 2.58
joystick_lower_threshold = 1.5


def scroll_mouse(up_threshold, low_threshold, config_flag, velocidad=1):
    if config_flag:
        return
    else:
        x = get_voltage(joystick_x)
        y = get_voltage(joystick_y)
    
        desplazamiento_x = 0
        desplazamiento_y = 0
    
        if x < low_threshold:
            desplazamiento_x = velocidad
        elif x > up_threshold:
            desplazamiento_x = -velocidad
        
        if y < low_threshold:
            desplazamiento_y = velocidad
        elif y > up_threshold:
            desplazamiento_y = -velocidad
        
        if desplazamiento_x != 0:
            keyboard.press(Keycode.SHIFT)
            mouse.move(wheel = desplazamiento_x)
            mouse.release_all()
            keyboard.release_all()
            time.sleep(0.05)
        if desplazamiento_y != 0:
            mouse.move(wheel=desplazamiento_y)
            mouse.release_all()

print(joystick_x.reference_voltage)


"""LEDS"""
# Pin asignado y tamaño de tira led
leds_pin = board.IO21
leds_size = 9
# Inicialización con NeoPixel, ajustando el brillo ya que estos leds son potentes y pueden deslumbrar
leds = neopixel.NeoPixel(leds_pin, leds_size, brightness=0.1, auto_write=False)

leds.show()

# Funciones de efectos para los leds
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
#         time.sleep(wait)

# Constantes para almacenar varios colores 
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

#rainbow()
    
""" Configuración de variables para la ejecución del firmware"""

# Esta parte la reservamos para guardar las macros y perfiles que deseemos
# Teclas asignadas a cada botón del teclado. Aquí podemos customizar las macros de cada tecla
default_macro_set = [
    [("Vol -",(ConsumerControlCode.VOLUME_DECREMENT,)), ("Play",(ConsumerControlCode.PLAY_PAUSE, )), ("Vol +", (ConsumerControlCode.VOLUME_INCREMENT,)) ],
    [("Mute", (ConsumerControlCode.MUTE,)), ("Bright -",(ConsumerControlCode.BRIGHTNESS_DECREMENT,)), ("Bright +",(ConsumerControlCode.BRIGHTNESS_INCREMENT,))],
    [("Snapshot", (Keycode.GUI, Keycode.SHIFT, Keycode.S )), ("ALT+TAB", (Keycode.ALT, Keycode.TAB)), ("CTRL+TAB",(Keycode.CONTROL, Keycode.TAB))]
    ]
default_macro_set2 = [
    [("Select Line",(Keycode.HOME, Keycode.SHIFT, Keycode.END)), ("Copy",(Keycode.CONTROL, Keycode.C)), ("Paste",(Keycode.CONTROL, Keycode.V)) ],
    [("Command Palette", (Keycode.CONTROL, Keycode.SHIFT, Keycode.P)), ("Run (no debug)",(Keycode.CONTROL, Keycode.F5)), ("Last Edit File",(Keycode.CONTROL, Keycode.K, Keycode.CONTROL, Keycode.Q))],
    [("Imports", ("import time \nimport board \nimport digitalio \nimport usb_hid")),
         ("Plantilla func", ("def mostrar_macro(nombre_macro): \n\tlcd.cursor_position(0,2)\n\tlcd.message = nombre_macro")),
         ("Nuevo fichero",(Keycode.CONTROL, Keycode.N))
     ]
    ]


# La estructura de cada layout es la siguiente: (Nombre, array con macros, color del perfil, color de highlight)
layouts = (("Perfil 1: Utils",default_macro_set, RED, GREEN),("Perfil 2: IDE", default_macro_set2, PURPLE, CYAN))


# Función para la configuración de nuevos perfiles macros, aparte de los predefinidos
def cargar_layouts_personalizados(ruta):
    nuevos_layouts = []
    
    with open(ruta, "r") as fichero:
        lineas = fichero.readlines()
    
    layout = {}
    macros = []
    
    def guardar_layout():
        if layout and macros:
            matriz = [macros[i:i+3] for i in range(0, len(macros), 3)]
            nuevos_layouts.append((
                layout["name"],
                matriz,
                layout["color"],
                layout["highlight"]
                ))
    for linea in lineas:
        linea.strip()
        
        #Saltamos linas vacías o comentarios
        if not linea or linea.startswith("#"):
            continue
        
        #Este fragmento funciona para guardar más de un perfil desde un mismo archivo txt
        if linea.startswith("[Perfil]"):
            guardar_layout() #Añado esto para el caso en que tengamos varios layouts en el mismo txt, 
            layout = {}      #así añadimos uno cada vez que empezamos el siguiente
            macros = []
            continue
        
        if linea.startswith("name"):
            layout["name"] = linea.split("=", 1)[1].strip()
            
        elif linea.startswith("color"):
            layout["color"] = tuple(map(int, linea.split("=")[1].split(",")))
        
        elif linea.startswith("highlight"):
            layout["highlight"] = tuple(map(int, linea.split("=")[1].split(",")))
        
        elif linea.startswith("macro"):
            _, macro = linea.split("=", 1)
            nombre, tipo, *valores = [x.strip() for x in macro.split(",")]
            
            if tipo == "text":
                string = ",".join(valores)         #Con esto, si la macro es un texto y contiene comas, obtenemos
                macros.append((nombre, string))    #la recreación correcta del texto. Inocuo para texto sin comas
            
            elif tipo == "keys":
                keys = []
                for valor in valores:
                    try:
                        keys.append(getattr(Keycode, valor))
                        print(getattr(Keycode, valor))
                    except AttributeError:
                        print(f"[!] Código inválido: {valor}")
                macros.append((nombre, tuple(keys)))
            
            elif tipo == "consumer":
                try:
                    macro = getattr(ConsumerControlCode, valores[0])
                    macros.append((nombre, (macro,)))
                except AttributeError:
                    print(f"[!] Código consumer inválido: {valores[0]}")
            
    guardar_layout()
    return nuevos_layouts

# Variable para controlar layout seleccionado
n_layout=0


config_inicial = mensaje_inicio(0.0001, "custom_layouts.txt")

layouts = list(layouts)
layouts.extend(config_inicial)
layouts = tuple(layouts)
    

# Bandera para entrar en modo cambio de perfil
config_flag = False
cambio_detectado = False # Esta bandera es necesaria para que al entrar en modo configuración no detectemos
                         # varios cambios con una misma inclinación del eje del joystick
                        
print(layouts)
# Bucle de ejecución
while True:
    
    scroll_mouse(joystick_upper_threshold, joystick_lower_threshold, config_flag)
    
    # Pulsación del botón del joystick para entrar en modo configuración de perfiles
    if not joystick_button.value:
        config_flag = not config_flag
        print("Boton pulsado")
        
    eje_x_joystick = get_voltage(joystick_x)
    # En este condicional, una vez activado el modo configuración, usamos el eje X del joystick para
    # recorrer los layouts disponibles hasta que volvamos a pulsar el botón para salir del modo y confirmar la selección
    # Este fragmento podría extraerse como función auxiliar del joystick
    if not cambio_detectado:
        if config_flag == True:
                if(eje_x_joystick > joystick_upper_threshold):
                    n_layout = (n_layout + 1) % len(layouts)
                    lcd.clear()
                    cambio_detectado = True
                elif(eje_x_joystick < joystick_lower_threshold):
                    n_layout = (n_layout - 1) % len(layouts)
                    lcd.clear()
                    cambio_detectado = True
    if joystick_lower_threshold < eje_x_joystick < joystick_upper_threshold :
        cambio_detectado = False
                
    print(get_voltage(joystick_x), get_voltage(joystick_y))
    
    # Aquí almacenamos en variables toda la información del perfil actual
    nombre_layout, layout_actual, color_layout, color_highlight = layouts[n_layout]

    # Rellenamos con los colores del layout
    leds.fill(color_layout)
    leds.show()
        
    # Mostramos perfil seleccionado en la LCD
    lcd.message = nombre_layout
    
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
                
                nombre_macro, macro = layout_actual[i][j]  # Acceso a la macro y su identificador
                
                # Mientras la fila este a 0 y tengamos una columna con el mismo valor
                # Tenemos el botón (i,j) pulsado
                while not row_pin.value and not col_pin.value:
                    #Mientras se pulsa el botón, se ilumina de otro color
                    leds[i*3+j*1] = color_highlight
                    leds.show()
                    mostrar_macro(nombre_macro) # Mostramos el identificador de la macro por la LCD
                    
                    pass  # Esperamos a que se deje de pulsar la tecla
                
                # Limpiamos la LCD dejando el perfil seleccionado
                lcd.clear()
                lcd.message = nombre_layout
                
                # Mandamos la combinación de teclas o escribir string en su caso                
                if isinstance(macro, str):  # Si es una string...
                    keyboard_layout.write(macro)  #  ... escribimos el string
                elif len(macro)>= 1:  # Si la macro contiene varias
                    print(macro, len(macro))
                    if(macro[0] in (111,112,205,226,234,233)) & len(macro) == 1: #Comprobamos si la macro maneja alguno de los códigos ConsumerControlCode. En caso de usar otros, añadirlos aquí
                        consumer_control.press(macro[0])
                        #time.sleep(0.5)
                        consumer_control.release()
                    for key in macro:
                        keyboard.press(key)  # ...se pulsan una a una y se sueltan juntas
                    keyboard.release_all()

                led.value = False # Apagamos el LED como fin de la pulsación
                
        row_pin.value = True # Volvemos a poner la fila en alto para comprobar la siguiente

    time.sleep(0.2)