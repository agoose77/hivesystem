keycodes = (
    "0",
    "1",
    "2",
    "3",
    "4",
    "5",
    "6",
    "7",
    "8",
    "9",
    "A",
    "ADD",
    "APOSTROPHE",
    "AT",
    "B",
    "BACK",  # Backspace
    "BACKSLASH",
    "C",
    "CAPITAL",  #Caps lock?
    "COLON",
    "COMMA",
    "D",
    "DELETE",
    "DIVIDE",
    "DOWN",
    "E",
    "END",
    "EQUALS",
    "ESCAPE",
    "F",
    "F1",
    "F10",
    "F11",
    "F12",
    "F13",
    "F14",
    "F15",
    "F2",
    "F3",
    "F4",
    "F5",
    "F6",
    "F7",
    "F8",
    "F9",
    "G",
    "GRAVE",
    "H",
    "HOME",
    "I",
    "INSERT",
    "J",
    "K",
    "L",
    "LBRACKET",
    "LCONTROL",
    "LEFT",
    "LMENU",  #Left Alt
    "LSHIFT",
    "M",
    "MINUS",
    "MULTIPLY",
    "N",
    "NUMLOCK",
    "NUMPAD0",
    "NUMPAD1",
    "NUMPAD2",
    "NUMPAD3",
    "NUMPAD4",
    "NUMPAD5",
    "NUMPAD6",
    "NUMPAD7",
    "NUMPAD8",
    "NUMPAD9",
    "NUMPADCOMMA",
    "NUMPADENTER",
    "NUMPADEQUALS",
    "O",
    "P",
    "PERIOD",
    "PGDOWN",
    "PGUP",
    "Q",
    "R",
    "RBRACKET",
    "RCONTROL",
    "RETURN",
    "RIGHT",
    "RMENU",  #Right Alt
    "RSHIFT",
    "S",
    "SCROLL",  #Scroll lock
    "SEMICOLON",
    "SLASH",
    "SPACE",
    "SUBTRACT",
    "T",
    "TAB",
    "U",
    "UNDERLINE",
    "UP",
    "V",
    "W",
    "X",
    "Y",
    "Z",
)

asciilist = {
    "ADD": '+',
    "BACKSLASH": '\\',
    "BACK": 8,
    "COLON": ':',
    "COMMA": ',',
    "DELETE": 127,
    "DIVIDE": '/',
    "EQUALS": '=',
    "ESCAPE": 27,
    "LBRACKET": '[',
    "MINUS": '-',
    "MULTIPLY": '*',
    "PERIOD": '.',
    "RBRACKET": ']',
    "RETURN": '\r',
    "SEMICOLON": ';',
    "SLASH": '/',
    "SPACE": 32,
    "SUBTRACT": '-',
    "TAB": 9,
    "UNDERLINE": '_',
}

for n in range(48, 123):
    asciilist[chr(n)] = n

ascii_to_keycode = {}
for key, value in asciilist.items():
    if isinstance(value, int):
        if value >= 97 and value <= 97 + 26:
            key = chr(ord(key) - 32)
        value = chr(value)
    ascii_to_keycode[value] = key

