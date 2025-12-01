# ============================================================================
# UI_RENDERER.PY - Renderizado LCD con Efectos Visuales
# PSIC-O-TRONIC - Animaciones y mejoras visuales
# ============================================================================

import time
from lcd_chars import convert_text, get_lives_display, load_custom_chars

# Constantes de timing (ms)
TRANSITION_SPEED = 50
CRT_LINE_DELAY = 30
BLINK_SPEED = 400


class LcdRenderer:
    """
    Renderizador de LCD con efectos visuales.
    Maneja buffer, transiciones y animaciones.
    """
    
    def __init__(self, lcd_hardware):
        """
        Args:
            lcd_hardware: Objeto I2cLcd físico
        """
        self.lcd = lcd_hardware
        self.width = 20
        self.height = 4
        
        # Buffer actual y shadow (para optimizar escrituras)
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.shadow = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        
        # Estado del LED de notificación
        self.led_on = False
        
        # Cargar caracteres custom
        load_custom_chars(self.lcd)
        
        # Frame counter para animaciones
        self.frame = 0
        
    def clear_buffer(self):
        """Limpia el buffer"""
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
    
    def put(self, x, y, text):
        """
        Escribe texto en el buffer.
        Convierte automáticamente caracteres especiales.
        """
        if y < 0 or y >= self.height:
            return
        
        safe_text = convert_text(text)
        for i, char in enumerate(safe_text):
            if 0 <= x + i < self.width:
                self.buffer[y][x + i] = char
    
    def put_centered(self, y, text):
        """Escribe texto centrado en una línea"""
        safe_text = convert_text(text)
        x = (self.width - len(safe_text)) // 2
        self.put(max(0, x), y, safe_text)
    
    def put_right(self, y, text):
        """Escribe texto alineado a la derecha"""
        safe_text = convert_text(text)
        x = self.width - len(safe_text)
        self.put(max(0, x), y, safe_text)
    
    def render(self, force=False):
        """
        Vuelca buffer al LCD físico.
        Solo escribe líneas que han cambiado (optimización I2C).
        """
        for y in range(self.height):
            if force or self.buffer[y] != self.shadow[y]:
                self.lcd.move_to(0, y)
                line = "".join(self.buffer[y])
                self.lcd.putstr(line)
                self.shadow[y] = self.buffer[y][:]
    
    def render_immediate(self, lines):
        """
        Renderiza líneas directamente sin buffer.
        Útil para mensajes rápidos.
        """
        self.lcd.clear()
        for i, line in enumerate(lines[:4]):
            safe_line = convert_text(line)
            self.lcd.move_to(0, i)
            self.lcd.putstr(safe_line[:20].ljust(20))
    
    # === EFECTOS DE TRANSICIÓN ===
    
    def transition_wipe_right(self, new_content):
        """
        Transición: barrido de izquierda a derecha.
        
        Args:
            new_content: Lista de 4 strings con nuevo contenido
        """
        for col in range(self.width + 1):
            for y in range(self.height):
                old_line = "".join(self.shadow[y])
                new_line = convert_text(new_content[y] if y < len(new_content) else "")
                new_line = new_line.ljust(self.width)
                
                # Mezclar: nuevo contenido hasta col, viejo después
                mixed = new_line[:col] + old_line[col:]
                
                self.lcd.move_to(0, y)
                self.lcd.putstr(mixed[:self.width])
            
            time.sleep_ms(TRANSITION_SPEED)
        
        # Actualizar shadow
        for y in range(self.height):
            new_line = convert_text(new_content[y] if y < len(new_content) else "")
            self.shadow[y] = list(new_line.ljust(self.width))
            self.buffer[y] = self.shadow[y][:]
    
    def transition_wipe_down(self, new_content):
        """Transición: barrido de arriba a abajo"""
        for row in range(self.height + 1):
            for y in range(self.height):
                if y < row:
                    # Nueva línea
                    line = convert_text(new_content[y] if y < len(new_content) else "")
                else:
                    # Línea antigua
                    line = "".join(self.shadow[y])
                
                self.lcd.move_to(0, y)
                self.lcd.putstr(line[:self.width].ljust(self.width))
            
            time.sleep_ms(TRANSITION_SPEED * 2)
        
        # Actualizar shadow
        for y in range(self.height):
            new_line = convert_text(new_content[y] if y < len(new_content) else "")
            self.shadow[y] = list(new_line.ljust(self.width))
            self.buffer[y] = self.shadow[y][:]
    
    def effect_crt_on(self, content):
        """
        Efecto: encendido tipo CRT/TV antigua.
        Líneas aparecen con efecto de escaneo.
        """
        # Fase 1: Línea horizontal en el centro
        self.lcd.clear()
        center_y = self.height // 2
        self.lcd.move_to(0, center_y)
        self.lcd.putstr("=" * self.width)
        time.sleep_ms(100)
        
        # Fase 2: Expandir verticalmente con ruido
        for expansion in range(1, center_y + 1):
            # Líneas de ruido expandiéndose
            for y in range(self.height):
                dist_from_center = abs(y - center_y)
                if dist_from_center <= expansion:
                    # Ruido aleatorio
                    noise = "".join([chr(0x20 + (i * 7 + y * 3 + expansion) % 15) 
                                    for i in range(self.width)])
                    self.lcd.move_to(0, y)
                    self.lcd.putstr(noise)
            time.sleep_ms(CRT_LINE_DELAY * 2)
        
        # Fase 3: Revelar contenido línea por línea
        for y in range(self.height):
            line = convert_text(content[y] if y < len(content) else "")
            self.lcd.move_to(0, y)
            self.lcd.putstr(line[:self.width].ljust(self.width))
            time.sleep_ms(CRT_LINE_DELAY)
        
        # Actualizar buffers
        for y in range(self.height):
            new_line = convert_text(content[y] if y < len(content) else "")
            self.shadow[y] = list(new_line.ljust(self.width))
            self.buffer[y] = self.shadow[y][:]
    
    def effect_blink_border(self, content, times=3):
        """
        Efecto: parpadeo de borde decorativo.
        """
        border_top = "+" + "-" * 18 + "+"
        border_bot = "+" + "-" * 18 + "+"
        
        for _ in range(times):
            # Con borde
            self.lcd.move_to(0, 0)
            self.lcd.putstr(border_top)
            self.lcd.move_to(0, 3)
            self.lcd.putstr(border_bot)
            time.sleep_ms(BLINK_SPEED // 2)
            
            # Sin borde (contenido normal)
            for y in range(self.height):
                line = convert_text(content[y] if y < len(content) else "")
                self.lcd.move_to(0, y)
                self.lcd.putstr(line[:self.width].ljust(self.width))
            time.sleep_ms(BLINK_SPEED // 2)
    
    def effect_message_alert(self, callback_led=None):
        """
        Efecto: alerta de nuevo mensaje (busca vibrando).
        
        Args:
            callback_led: Función para controlar LED (recibe bool)
        """
        alert_frames = [
            ["+------------------+",
             "  *MENSAJE NUEVO*  ",
             "                    ",
             "+------------------+"],
            ["+------------------+",
             " * MENSAJE NUEVO * ",
             "                    ",
             "+------------------+"],
        ]
        
        for i in range(6):
            frame = alert_frames[i % 2]
            for y, line in enumerate(frame):
                self.lcd.move_to(0, y)
                self.lcd.putstr(line)
            
            if callback_led:
                callback_led(i % 2 == 0)
            
            time.sleep_ms(150)
        
        if callback_led:
            callback_led(False)
    
    def effect_hearts_pulse(self, lives, max_lives=3):
        """
        Efecto: corazones que laten (cuando quedan pocas vidas).
        Solo activo si lives <= 1.
        """
        if lives > 1:
            return get_lives_display(lives, max_lives)
        
        # Efecto latido
        self.frame += 1
        if (self.frame // 4) % 2 == 0:
            # Corazón "grande" (lleno)
            return get_lives_display(lives, max_lives)
        else:
            # Corazón "pequeño" (simular con espacio)
            filled = chr(0) * lives
            empty = chr(1) * (max_lives - lives)
            # Alternar el último corazón
            if lives > 0:
                return chr(1) + filled[1:] + empty if len(filled) > 0 else empty
            return empty
    
    # === FRAMES DECORATIVOS ===
    
    def draw_frame_simple(self):
        """Dibuja marco simple en los bordes"""
        self.put(0, 0, "+")
        self.put(19, 0, "+")
        self.put(0, 3, "+")
        self.put(19, 3, "+")
        for i in range(1, 19):
            self.buffer[0][i] = '-'
            self.buffer[3][i] = '-'
        for y in range(1, 3):
            self.buffer[y][0] = '|'
            self.buffer[y][19] = '|'
    
    def draw_frame_double(self):
        """Dibuja marco doble"""
        self.put(0, 0, "====================")
        self.put(0, 3, "====================")
    
    # === UTILIDADES ===
    
    def create_progress_bar(self, progress, width=20, filled='#', empty='.'):
        """
        Crea una barra de progreso.
        
        Args:
            progress: Valor 0.0 a 1.0
            width: Ancho en caracteres
            
        Returns:
            String con la barra
        """
        filled_count = int(progress * width)
        return filled * filled_count + empty * (width - filled_count)
    
    def wrap_text(self, text, width=20):
        """
        Divide texto largo en líneas.
        
        Args:
            text: Texto a dividir
            width: Ancho máximo por línea
            
        Returns:
            Lista de strings
        """
        safe_text = convert_text(text)
        words = safe_text.split()
        lines = []
        current = ""
        
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current += (word + " ") if current else word
            else:
                if current:
                    lines.append(current.strip())
                current = word + " "
        
        if current.strip():
            lines.append(current.strip())
        
        return lines if lines else [""]
    
    def get_buffer_as_strings(self):
        """Retorna el buffer actual como lista de strings (para debug)"""
        return ["".join(row) for row in self.buffer]


class DebugRenderer:
    """
    Renderizador de debug que imprime en consola.
    Útil para desarrollo sin hardware.
    """
    
    def __init__(self):
        self.width = 20
        self.height = 4
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
        self.led_on = False
        self.frame = 0
    
    def clear_buffer(self):
        self.buffer = [[' ' for _ in range(self.width)] for _ in range(self.height)]
    
    def put(self, x, y, text):
        if y < 0 or y >= self.height:
            return
        safe_text = convert_text(text)
        for i, char in enumerate(safe_text):
            if 0 <= x + i < self.width:
                # Convertir chars custom a símbolos visibles
                if ord(char) < 8:
                    char = ['♥', '♡', 'á', 'é', 'í', 'ó', 'ú', 'ñ'][ord(char)]
                self.buffer[y][x + i] = char
    
    def put_centered(self, y, text):
        safe_text = convert_text(text)
        x = (self.width - len(safe_text)) // 2
        self.put(max(0, x), y, safe_text)
    
    def render(self, force=False):
        led_char = "*" if self.led_on else " "
        print(f"\n[LCD] LED:{led_char}")
        print("+" + "-"*20 + "+")
        for row in self.buffer:
            line = "".join(row)
            # Convertir chars custom
            for i in range(8):
                line = line.replace(chr(i), ['♥','♡','á','é','í','ó','ú','ñ'][i])
            print(f"|{line}|")
        print("+" + "-"*20 + "+")
    
    def render_immediate(self, lines):
        self.clear_buffer()
        for i, line in enumerate(lines[:4]):
            self.put(0, i, line)
        self.render()
    
    # Métodos stub para efectos
    def transition_wipe_right(self, content):
        self.render_immediate(content)
    
    def transition_wipe_down(self, content):
        self.render_immediate(content)
    
    def effect_crt_on(self, content):
        print("[EFFECT] CRT ON")
        self.render_immediate(content)
    
    def effect_message_alert(self, callback_led=None):
        print("[EFFECT] Message Alert")
    
    def effect_hearts_pulse(self, lives, max_lives=3):
        return '♥' * lives + '♡' * (max_lives - lives)
    
    def wrap_text(self, text, width=20):
        words = text.split()
        lines = []
        current = ""
        for word in words:
            if len(current) + len(word) + 1 <= width:
                current += (word + " ") if current else word
            else:
                if current:
                    lines.append(current.strip())
                current = word + " "
        if current.strip():
            lines.append(current.strip())
        return lines if lines else [""]
    
    def create_progress_bar(self, progress, width=20):
        filled = int(progress * width)
        return '#' * filled + '.' * (width - filled)


# Test standalone
if __name__ == "__main__":
    print("=== Test UI Renderer (Debug Mode) ===")
    
    renderer = DebugRenderer()
    
    # Test básico
    renderer.clear_buffer()
    renderer.put_centered(0, "== MENU ==")
    renderer.put(1, 1, ">Jugar")
    renderer.put(1, 2, " Opciones")
    renderer.put(1, 3, " Créditos")
    renderer.render()
    
    # Test con caracteres especiales
    print("\n--- Con caracteres especiales ---")
    renderer.clear_buffer()
    renderer.put(0, 0, "Señor Psicólogo")
    renderer.put(0, 1, "Vidas: ♥♥♡")
    renderer.put(0, 2, "¿Cómo está?")
    renderer.render()
    
    # Test wrap text
    print("\n--- Wrap Text ---")
    long_text = "Este es un texto muy largo que debe dividirse en varias líneas"
    lines = renderer.wrap_text(long_text)
    for line in lines:
        print(f"  |{line}|")
    
    # Test progress bar
    print("\n--- Progress Bar ---")
    for p in [0, 0.25, 0.5, 0.75, 1.0]:
        bar = renderer.create_progress_bar(p)
        print(f"  {int(p*100):3d}%: {bar}")
