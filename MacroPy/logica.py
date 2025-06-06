import time
import json
from pynput import keyboard
from pynput.keyboard import Controller, Key

controller = Controller()

macro = []
current_keys = set()
stop_macro = False

def on_press(key):
    current_keys.add(key)

def on_release(key):
    global stop_macro

    # Captura la combinación actual y la guarda
    if key == Key.esc:
        # Termina la grabación
        return False
    elif key == Key.f12:
        # Marca para detener la reproducción
        stop_macro = True
        return False
    else:
        # Guardar combinación al soltar la última tecla
        if current_keys:
            combo = [str(k) for k in current_keys]
            macro.append(combo)
            print(f"Combinación capturada: {combo}")
            current_keys.clear()

def grabar_macro():
    print("Presiona combinaciones de teclas que quieres grabar. Pulsa 'ESC' para terminar.")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

def guardar_macro(nombre_archivo):
    with open(nombre_archivo, 'w') as f:
        json.dump(macro, f)
    print(f"Macro guardado en {nombre_archivo}")

def cargar_macro(nombre_archivo):
    with open(nombre_archivo, 'r') as f:
        return json.load(f)

def presionar_combinacion(combinacion):
    for tecla in combinacion:
        if "Key." in tecla:
            tecla_obj = getattr(Key, tecla.replace("Key.", ""))
            controller.press(tecla_obj)
        else:
            controller.press(tecla.replace("'", ""))
    for tecla in reversed(combinacion):
        if "Key." in tecla:
            tecla_obj = getattr(Key, tecla.replace("Key.", ""))
            controller.release(tecla_obj)
        else:
            controller.release(tecla.replace("'", ""))

def reproducir_macro(macro, tiempo_entre, repeticiones=None):
    global stop_macro
    stop_macro = False

    def detener_macro(key):
        global stop_macro
        if key == Key.f12:
            stop_macro = True
            return False

    listener = keyboard.Listener(on_press=detener_macro)
    listener.start()

    contador = 0
    while True:
        for combinacion in macro:
            if stop_macro:
                listener.stop()
                return
            presionar_combinacion(combinacion)
            print(f"Combinación enviada: {combinacion}")
            time.sleep(tiempo_entre)

        if repeticiones is not None:
            contador += 1
            if contador >= repeticiones:
                break

    listener.stop()

if __name__ == "__main__":
    modo = input("¿Qué quieres hacer? (1 = Grabar Macro, 2 = Cargar y Reproducir Macro): ")

    if modo == "1":
        grabar_macro()
        nombre = input("Nombre del archivo para guardar el macro (ejemplo: mi_macro.json): ")
        guardar_macro(nombre)

    elif modo == "2":
        nombre = input("Nombre del archivo del macro a cargar (ejemplo: mi_macro.json): ")
        macro_cargado = cargar_macro(nombre)

        tiempo = float(input("¿Tiempo entre combinaciones (segundos)? (Ej: 0.5): "))
        repeticiones = input("¿Cuántas veces repetir? (vacío para infinito): ")
        if repeticiones.strip() == "":
            repeticiones = None
        else:
            repeticiones = int(repeticiones)

        print("Empezando en 3 segundos... Presiona F12 para detener en cualquier momento.")
        time.sleep(3)

        reproducir_macro(macro_cargado, tiempo, repeticiones)
