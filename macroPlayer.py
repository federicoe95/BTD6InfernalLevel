import json
import time
import pyautogui
import threading

from pynput import keyboard
from pynput.mouse import Controller as MouseController

FILE_INPUT = "macro.json"
TRIGGER_IMAGE = "trigger.png"

EXTRA_CLICK_1 = (100, 200)
EXTRA_CLICK_2 = (300, 400)

pyautogui.FAILSAFE = True

mouse = MouseController()

stop = False

# stato trigger (per evitare ripetizioni continue)
trigger_visible = False


# -------------------
# STOP EMERGENZA (ESC)
# -------------------

def on_press(key):
    global stop

    if key == keyboard.Key.esc:
        stop = True
        print("🛑 STOP RICHIESTO (ESC)")
        return False


listener = keyboard.Listener(on_press=on_press)
listener.start()


# -------------------
# CONTROLLO SCHERMATA SPECIALE
# -------------------

def check_special_screen():
    global trigger_visible

    try:
        found = pyautogui.locateOnScreen(
            TRIGGER_IMAGE,
            confidence=0.95
        )

        currently_visible = found is not None

        if currently_visible and not trigger_visible:

            print("🎯 Schermata speciale rilevata")

            pyautogui.click(*EXTRA_CLICK_1)
            time.sleep(0.1)
            pyautogui.click(*EXTRA_CLICK_2)

            print("✅ Click extra eseguiti")

        trigger_visible = currently_visible

    except Exception as e:
        print(f"Errore riconoscimento immagine: {e}")


# -------------------
# THREAD WATCHER
# -------------------

def screen_watcher():
    while not stop:
        check_special_screen()
        time.sleep(1)


watcher_thread = threading.Thread(target=screen_watcher, daemon=True)
watcher_thread.start()


# -------------------
# CARICA MACRO
# -------------------

with open(FILE_INPUT, "r", encoding="utf-8") as f:
    macro = json.load(f)


print("▶ Avvio macro (loop infinito) tra 3 secondi...")
time.sleep(3)


# -------------------
# LOOP INFINITO MACRO
# -------------------

while not stop:

    last_t = 0

    for ev in macro:

        if stop:
            break

        t = ev["t"]
        delay = t - last_t

        if delay > 0:
            time.sleep(delay)

        typ = ev["type"]

        # -------------------
        # CLICK
        # -------------------
        if typ == "click":

            x = ev["x"]
            y = ev["y"]

            pyautogui.click(x, y)
            print(f"🖱 click {x},{y}")

        # -------------------
        # SCROLL
        # -------------------
        elif typ == "scroll":

            dy = ev.get("dy", 0)

            mouse.scroll(0, dy)
            print(f"📜 scroll {dy}")

        # -------------------
        # TASTI
        # -------------------
        elif typ == "key":

            key = ev["key"]

            if "Key." in key:
                key_name = key.replace("Key.", "")
                try:
                    pyautogui.press(key_name)
                except:
                    pass
            else:
                pyautogui.write(key)

            print(f"⌨ {key}")

        last_t = t

    print("🔄 Macro terminata → riavvio...")


print("\n🛑 Script fermato")