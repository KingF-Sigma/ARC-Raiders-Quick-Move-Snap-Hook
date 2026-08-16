import ctypes
import time

# Win32 API Konstanten
MOUSEEVENTF_MOVE = 0x0001
MOUSEEVENTF_LEFTDOWN = 0x0002
MOUSEEVENTF_LEFTUP = 0x0004
MOUSEEVENTF_ABSOLUTE = 0x8000

class MOUSEINPUT(ctypes.Structure):
    _fields_ = [
        ("dx", ctypes.c_long),
        ("dy", ctypes.c_long),
        ("mouseData", ctypes.c_ulong),
        ("dwFlags", ctypes.c_ulong),
        ("time", ctypes.c_ulong),
        ("dwExtraInfo", ctypes.POINTER(ctypes.c_ulong))
    ]

class INPUT(ctypes.Structure):
    class _INPUT(ctypes.Union):
        _fields_ = [("mi", MOUSEINPUT)]
    _anonymous_ = ("_input",)
    _fields_ = [
        ("type", ctypes.c_ulong),
        ("_input", _INPUT)
    ]

def send_input(input_struct):
    ctypes.windll.user32.SendInput(1, ctypes.byref(input_struct), ctypes.sizeof(input_struct))

def move_mouse(x, y):
    # Umrechnung in absolute Win32-Koordinaten (0 bis 65535)
    screen_width = ctypes.windll.user32.GetSystemMetrics(0)
    screen_height = ctypes.windll.user32.GetSystemMetrics(1)
    
    abs_x = int(x * 65535 / screen_width)
    abs_y = int(y * 65535 / screen_height)
    
    inp = INPUT()
    inp.type = 0  # INPUT_MOUSE
    inp.mi.dx = abs_x
    inp.mi.dy = abs_y
    inp.mi.dwFlags = MOUSEEVENTF_MOVE | MOUSEEVENTF_ABSOLUTE
    send_input(inp)

def mouse_down():
    inp = INPUT()
    inp.type = 0
    inp.mi.dwFlags = MOUSEEVENTF_LEFTDOWN
    send_input(inp)

def mouse_up():
    inp = INPUT()
    inp.type = 0
    inp.mi.dwFlags = MOUSEEVENTF_LEFTUP
    send_input(inp)

def move_item(start_x, start_y, end_x, end_y, delay_ms):
    delay_sec = delay_ms / 1000.0
    
    # 1. Zum Start-Slot bewegen
    move_mouse(start_x, start_y)
    time.sleep(delay_sec)
    
    # 2. Item greifen (Drag)
    mouse_down()
    time.sleep(delay_sec)
    
    # 3. Zum Ziel-Slot bewegen
    move_mouse(end_x, end_y)
    time.sleep(delay_sec)
    
    # 4. Item ablegen (Drop)
    mouse_up()
    time.sleep(delay_sec)