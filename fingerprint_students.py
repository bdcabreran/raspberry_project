import time
import adafruit_fingerprint

# import board
import busio
from digitalio import DigitalInOut, Direction

# led = DigitalInOut(board.D13)
# led.direction = Direction.OUTPUT
# uart = busio.UART(board.TX, board.RX, baudrate=57600)

# If using with a computer such as Linux/RaspberryPi, Mac, Windows with USB/serial converter:
import serial
uart = serial.Serial("/dev/ttyAMA0", baudrate=57600, timeout=1)
finger = adafruit_fingerprint.Adafruit_Fingerprint(uart)
##################################################

def get_fingerprint():
    """Obtenga una imagen de huella digital, modifíquela y vea si coincide."""
    print("Esperando por Imagen ...")
    while finger.get_image() != adafruit_fingerprint.OK:
        pass
    print("Obteniendo plantilla...")
    if finger.image_2_tz(1) != adafruit_fingerprint.OK:
        return False
    print("Buscando...")
    if finger.finger_search() != adafruit_fingerprint.OK:
        return False
    return True


# pylint: disable=too-many-branches
def get_fingerprint_detail():
    """Obtenga una imagen de huella digital, modifíquela y vea si coincide.
    Esta vez, imprima cada error en lugar de simplemente regresar en caso de falla"""
    print("Obteniendo imagen...", end="", flush=True)
    i = finger.get_image()
    if i == adafruit_fingerprint.OK:
        print("Imagen Tomada")
    else:
        if i == adafruit_fingerprint.NOFINGER:
            print("Huella no detectada")
        elif i == adafruit_fingerprint.IMAGEFAIL:
            print("Error de Imagen")
        else:
            print("Otro Error")
        return False

    print("Obteniendo Plantilla...", end="", flush=True)
    i = finger.image_2_tz(1)
    if i == adafruit_fingerprint.OK:
        print("Plantilla completa")
    else:
        if i == adafruit_fingerprint.IMAGEMESS:
            print("Imagen distorsionada")
        elif i == adafruit_fingerprint.FEATUREFAIL:
            print("No se pudo identificar caracteristicas")
        elif i == adafruit_fingerprint.INVALIDIMAGE:
            print("Imagen Invalida")
        else:
            print("Otro Error")
        return False

    print("Buscando...", end="", flush=True)
    i = finger.finger_fast_search()
    # pylint: disable=no-else-return
    # This block needs to be refactored when it can be tested.
    if i == adafruit_fingerprint.OK:
        print("Huella encontrada!")
        return True
    else:
        if i == adafruit_fingerprint.NOTFOUND:
            print("No se encontraron coincidencias")
        else:
            print("Otro Error")
        return False


# pylint: disable=too-many-statements
def enroll_finger(location):
    """Tome  2 imágenes de un dedo,  modifíquelas, luego guárdelas en 'location'"""
    for fingerimg in range(1, 3):
        if fingerimg == 1:
            print("Coloque el dedo en el sensor..", end="", flush=True)
        else:
            print("Coloque el dedo en el sensor otra vez..", end="", flush=True)

        while True:
            i = finger.get_image()

            if i == adafruit_fingerprint.OK:
                print("Imagen Tomada")
                break
            if i == adafruit_fingerprint.NOFINGER:
                print(".", end="", flush=True)
            elif i == adafruit_fingerprint.IMAGEFAIL:
                print("Error de Imagen")
                return False
            else:
                print("Otro error")
                return False

        print("Tomando plantilla...", end="", flush=True)
        i = finger.image_2_tz(fingerimg)
        if i == adafruit_fingerprint.OK:
            print("completado")
        else:
            if i == adafruit_fingerprint.IMAGEMESS:
                print("Imagen distorsionada")
            elif i == adafruit_fingerprint.FEATUREFAIL:
                print("No se pudo identificar caracteristicas")
            elif i == adafruit_fingerprint.INVALIDIMAGE:
                print("Imagen Invalida")
            else:
                print("Otro Error")
            return False

        if fingerimg == 1:
            print("Remueva el dedo")
            time.sleep(1)
            while i != adafruit_fingerprint.NOFINGER:
                i = finger.get_image()

    print("Creando modelo...", end="", flush=True)
    i = finger.create_model()
    if i == adafruit_fingerprint.OK:
        print("Creado")
    else:
        if i == adafruit_fingerprint.ENROLLMISMATCH:
            print("las huellas no coinciden")
        else:
            print("Otro error")
        return False

    print("Almacenando modelo #%d..." % location, end="", flush=True)
    i = finger.store_model(location)
    if i == adafruit_fingerprint.OK:
        print("Almacenado")
    else:
        if i == adafruit_fingerprint.BADLOCATION:
            print("Error de almacenamiendo")
        elif i == adafruit_fingerprint.FLASHERR:
            print("Error de almacenamiento en flash ")
        else:
            print("Otro error")
        return False

    return True


##################################################

def get_num():
    """Usar input() para obtener un numero de 1 to 127. repta hasta que sea exitoso!"""
    i = 0
    while (i > 127) or (i < 1):
        try:
            i = int(input("Ingresar ID # rango 1-127: "))
        except ValueError:
            pass
    return i


while True:
    print("----------------")
    if finger.read_templates() != adafruit_fingerprint.OK:
        raise RuntimeError("Error al leer plantillas")
    print("Plantillas de huellas :", finger.templates)
    print("e) Inscribir nueva huella")
    print("f) Detectar huella")
    print("d) Borrar Huella")
    print("----------------")
    c = input("> ")

    if c == "e":
        enroll_finger(get_num())
    if c == "f":
        if get_fingerprint():
            print("Huella Encontrada #", finger.finger_id, "con exactitud", finger.confidence)
        else:
            print("Huella no Encontrada")
    if c == "d":
        if finger.delete_model(get_num()) == adafruit_fingerprint.OK:
            print("Huella eliminada con exito!")
        else:
            print("Error al borrar")