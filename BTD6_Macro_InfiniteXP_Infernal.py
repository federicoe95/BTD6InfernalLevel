from pynput import mouse, keyboard
import time
import json
import threading

FILE_OUTPUT = "macro.json"

eventi = []
start_time = time.time()

running = True
paused = False


def tempo():
    return round(time.time() - start_time, 4)


# -------------------
# EVENTI MOUSE
# -------------------

def on_click(x, y, button, pressed):
    if not running or paused:
        return

    if pressed:
        eventi.append({
            "t": tempo(),
            "type": "click",
            "x": x,
            "y": y,
            "button": str(button)
        })
        print(eventi[-1])


def on_scroll(x, y, dx, dy):
    if not running or paused:
        return

    eventi.append({
        "t": tempo(),
        "type": "scroll",
        "dy": dy
    })

    print(f"scroll {dy}")


# -------------------
# EVENTI TASTIERA
# -------------------

def on_press(key):
    global running, paused

    try:
        k = key.char
    except:
        k = str(key)

    # F8 = pause/resume
    if key == keyboard.Key.f8:
        paused = not paused
        print("⏸ PAUSA" if paused else "▶ RIPRESA")
        return

    # F12 = stop
    if key == keyboard.Key.f12:
        running = False
        print("🛑 STOP REGISTRAZIONE")
        return False

    if not running or paused:
        return

    eventi.append({
        "t": tempo(),
        "type": "key",
        "key": k
    })
    print(eventi[-1])


# -------------------
# THREAD LISTENER
# -------------------

print("🎥 Registrazione avviata")
print("F8 = pausa / riprendi | F12 = stop e salva\n")

mouse_listener = mouse.Listener(
    on_click=on_click,
    on_scroll=on_scroll
)

keyboard_listener = keyboard.Listener(
    on_press=on_press
)

mouse_listener.start()
keyboard_listener.start()

keyboard_listener.join()
mouse_listener.stop()


# -------------------
# SALVATAGGIO FILE
# -------------------

with open(FILE_OUTPUT, "w", encoding="utf-8") as f:
    json.dump(eventi, f, indent=2)

print(f"\n💾 Salvato in {FILE_OUTPUT}")