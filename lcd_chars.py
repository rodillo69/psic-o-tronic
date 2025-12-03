# ============================================================================
# LCD_CHARS.PY - Caracteres Custom para LCD HD44780
# PSIC-O-TRONIC - Caracteres españoles y símbolos especiales
# ============================================================================
# El LCD HD44780 permite 8 caracteres custom (CGRAM 0x00-0x07)
# Cada carácter es una matriz de 5x8 píxeles
# ============================================================================

# Definición de caracteres custom (5 columnas x 8 filas)
# 1 = pixel encendido, 0 = pixel apagado

CUSTOM_CHARS = {
    # Slot 0: Corazón lleno ♥
    'heart_full': [
        0b00000,
        0b01010,
        0b11111,
        0b11111,
        0b11111,
        0b01110,
        0b00100,
        0b00000,
    ],
    
    # Slot 1: Corazón vacío ♡
    'heart_empty': [
        0b00000,
        0b01010,
        0b10101,
        0b10001,
        0b10001,
        0b01010,
        0b00100,
        0b00000,
    ],
    
    # Slot 2: á (a con acento)
    'a_acute': [
        0b00010,
        0b00100,
        0b01110,
        0b00001,
        0b01111,
        0b10001,
        0b01111,
        0b00000,
    ],
    
    # Slot 3: é (e con acento)
    'e_acute': [
        0b00010,
        0b00100,
        0b01110,
        0b10001,
        0b11111,
        0b10000,
        0b01110,
        0b00000,
    ],
    
    # Slot 4: í (i con acento)
    'i_acute': [
        0b00010,
        0b00100,
        0b00000,
        0b01100,
        0b00100,
        0b00100,
        0b01110,
        0b00000,
    ],
    
    # Slot 5: ó (o con acento)
    'o_acute': [
        0b00010,
        0b00100,
        0b01110,
        0b10001,
        0b10001,
        0b10001,
        0b01110,
        0b00000,
    ],
    
    # Slot 6: ú (u con acento)
    'u_acute': [
        0b00010,
        0b00100,
        0b10001,
        0b10001,
        0b10001,
        0b10011,
        0b01101,
        0b00000,
    ],
    
    # Slot 7: ñ (eñe)
    'n_tilde': [
        0b01010,
        0b00100,
        0b10110,
        0b11001,
        0b10001,
        0b10001,
        0b10001,
        0b00000,
    ],
}

# Mapeo de slot a nombre
CHAR_SLOTS = {
    0: 'heart_full',
    1: 'heart_empty', 
    2: 'a_acute',
    3: 'e_acute',
    4: 'i_acute',
    5: 'o_acute',
    6: 'u_acute',
    7: 'n_tilde',
}

# Mapeo de carácter Unicode a slot LCD
UNICODE_TO_LCD = {
    '♥': chr(0),
    '♡': chr(1),
    'á': chr(2),
    'Á': chr(2),  # Mayúscula usa mismo char
    'é': chr(3),
    'É': chr(3),
    'í': chr(4),
    'Í': chr(4),
    'ó': chr(5),
    'Ó': chr(5),
    'ú': chr(6),
    'Ú': chr(6),
    'ñ': chr(7),
    'Ñ': chr(7),
}

# Caracteres que se mantienen como ASCII (fallback)
# ¿ y ¡ se eliminan (cadena vacía) porque no los queremos
FALLBACK_CHARS = {
    '¿': '',
    '¡': '',
    'ü': 'u',
    'Ü': 'U',
    '€': 'E',
    '£': 'L',
    '"': '"',
    '"': '"',
    ''': "'",
    ''': "'",
    '—': '-',
    '–': '-',
    '…': '...',
    '★': '*',
    '●': 'o',
    '→': '>',
    '←': '<',
    '↑': '^',
    '↓': 'v',
}


def load_custom_chars(lcd):
    """
    Carga los caracteres custom en la CGRAM del LCD.
    Debe llamarse después de inicializar el LCD.
    
    Args:
        lcd: Objeto I2cLcd inicializado
    """
    for slot, name in CHAR_SLOTS.items():
        char_data = CUSTOM_CHARS[name]
        lcd.custom_char(slot, bytearray(char_data))


def convert_text(text):
    """
    Convierte texto con caracteres especiales a formato LCD.
    Reemplaza vocales acentuadas y ñ por caracteres custom,
    y otros caracteres especiales por sus equivalentes ASCII.
    También elimina signos de puntuación al inicio.
    
    Args:
        text: String con posibles caracteres especiales
        
    Returns:
        String compatible con LCD
    """
    if text is None:
        return ""
    
    # Limpiar signos al inicio
    text = str(text).lstrip('!?¡¿ ')
    
    result = []
    for char in text:
        if char in UNICODE_TO_LCD:
            # Carácter custom disponible
            result.append(UNICODE_TO_LCD[char])
        elif char in FALLBACK_CHARS:
            # Fallback a ASCII (¿¡ se eliminan porque son '')
            fb = FALLBACK_CHARS[char]
            if fb:  # Solo añadir si no es cadena vacía
                result.append(fb)
        elif ord(char) < 128:
            # ASCII estándar
            result.append(char)
        else:
            # Carácter desconocido
            result.append('?')
    
    return "".join(result)


def get_heart_char(filled=True):
    """Retorna el carácter de corazón lleno o vacío"""
    return chr(0) if filled else chr(1)


def get_lives_display(current_lives, max_lives=3):
    """
    Genera string de vidas con corazones.
    Ej: 2 de 3 vidas = "♥♥♡"
    
    Args:
        current_lives: Vidas actuales
        max_lives: Vidas máximas
        
    Returns:
        String con corazones
    """
    filled = chr(0) * current_lives
    empty = chr(1) * (max_lives - current_lives)
    return filled + empty


# Test standalone
if __name__ == "__main__":
    print("=== Test LCD Chars ===")
    
    # Test conversión
    test_strings = [
        "Hola señor",
        "¿Cómo está?",
        "Psicólogo loco",
        "Vidas: ♥♥♡",
    ]
    
    for s in test_strings:
        converted = convert_text(s)
        print(f"Original: {s}")
        print(f"Convertido: {repr(converted)}")
        print()
    
    # Test vidas
    for lives in range(4):
        display = get_lives_display(lives, 3)
        print(f"Vidas {lives}/3: {repr(display)}")
