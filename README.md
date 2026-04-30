# Educational Keylogger that runs *locally*

## A lightweight Windows keylogger wrotten in Python. Designed to capture every keystroke!

# Legal and Ethical Disclaimer

**This tool is provided strictly for educational, personal, and authorized testing purposes.**  

Using a keylogger on a device without explicit, documented consent from the owner is illegal in most jurisdictions. The author assumes no responsibility for misuse, data breaches or legal consequences. Always comply with local laws and obtain proper authorization before deploying monitoring software.

## Overview
A Windows keyboard input analyzer designed to demonstrate how the operating system translates physical keystrokes into usable Unicode characters. The script captures global input and every keyboard layouts, with proper handling and automtic organization by activelly stating each window/application used.

##Features
- Global keystroke capture with automatic application window tracking
- Unicode characters using native Windows APIs
- Proper handling of Shift, Caps Lock, and Ctrl modifier combinations
- Clean mapping for function keys, navigation keys, and system keys
- Real-time console output with persistent UTF-8 file logging
- Automatic log segmentation using visual separators when window focus changes
- Termintaion of program using the ESC key
- Cross-layout compatibility (AZERTY, QWERTY etc.)

## Technical Architecture

The script bypasses naive virtual keu mapping by implementing the official Windows input translation pipeline:

- Window Context Detection
`GetForegroundWindow` retrieves the handle of the active window. `GetWindowThreadProcessId` and `GetKeyboardLayout` extract the thread-specific input layout, ensuring the correct locale mapping is used for translation.
- Keyboard State Capture
`GetKeyboardState` populates a 256-byte array with the current status of all virtual keys. This is required for accurate dead-key handling, modifier combinations, and layout-aware translation.
- Virtual Key to Scan Code Translation
`MapVirtualKeyExW` converts a logical virtual key code into a hardware scan code using the active window's layout. Scan codes represent physical key positions rather than logical characters.
- Unicode Resolution
`ToUnicodeEx` combines the virtual key, scan code, keyboard state, and layout identifier to produce the exact Unicode character the user expects. This approach correctly handles dead keys, composition sequences, and non-ASCII layouts where `chr(vk_code)` would fail.
- Modifier Logic
Shift and Caps Lock states are evaluated using XOR logic to determine capitalization rules across all keyboard layouts. Ctrl combinations are intercepted and formatted explicitly.
- Special Key Handling
System and function keys are intercepted before reaching the Unicode translation pipeline. This prevents control characters, null bytes, or console rendering artifacts from appearing in logs.

## Output Format

Logs are automatically segmented by active window. Each section is separated by a visual marker containing the window title. Keystrokes are timestamped and written in chronological order.

Example log structure:
```
====== Untitled - Notepad ======
[14:32:01] [ESC]
[14:32:03] [F1]
[14:32:05] a
[14:32:06] [TAB]
[14:32:08] [CTRL+C]

====== Google Chrome ======
[14:32:15] g
[14:32:16] o
[14:32:17] o
[14:32:18] g
[14:32:19] l
[14:32:19] e
```
## Security and Educational Notes

- Defensive Context: This pipeline mirrors how legitimate accessibility tools, password managers, and input method editors process keyboard input. Understanding it helps security professionals differentiate between documented API usage and malicious hooking techniques in forensic analysis.

- Detection Surface: The script uses documented, query-based user32 functions. It does not install global hooks, inject code, modify system state, making it suitable for studying input behavior without triggering malware heuristics.

- Hardware Limitations: The Fn key is processed at the keyboard controller level and never generates a scan code or virtual key event at the OS level, therefore cannot be captured by any standard Windows API.

- Dead Key Behavior: ToUnicodeEx consumes the dead key buffer on the first press (e.g. pressing an accent key logs nothing until a base character follows).

- Log Management: The log file grows continuously during execution. Clear or rotate input_log.txt manually if storage becomes a concern.

