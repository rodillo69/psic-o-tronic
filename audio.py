"""
PSIC-O-TRONIC - Sistema de Audio 8-bit
Sonidos estilo chiptune/Game Boy usando PWM
Version 2.4: Audio no-bloqueante con timers
"""

from machine import Pin, PWM, Timer
import time

# Notas musicales (frecuencias en Hz)
NOTAS = {
    'C3': 131, 'D3': 147, 'E3': 165, 'F3': 175, 'G3': 196, 'A3': 220, 'B3': 247,
    'C4': 262, 'D4': 294, 'E4': 330, 'F4': 349, 'G4': 392, 'A4': 440, 'B4': 494,
    'C5': 523, 'D5': 587, 'E5': 659, 'F5': 698, 'G5': 784, 'A5': 880, 'B5': 988,
    'C6': 1047, 'D6': 1175, 'E6': 1319, 'F6': 1397, 'G6': 1568,
    '_': 0  # Silencio
}

# Melodias predefinidas: lista de (nota, duracion_ms)
MELODIAS = {
    # Inicio del juego - fanfarria épica
    'intro': [
        ('C4', 100), ('E4', 100), ('G4', 100), ('C5', 200),
        ('_', 50),
        ('G4', 100), ('C5', 300)
    ],
    
    # Mensaje nuevo - notificación
    'mensaje': [
        ('E5', 80), ('G5', 80), ('E5', 80), ('C5', 120)
    ],
    
    # Respuesta correcta - ascendente alegre
    'correcto': [
        ('C5', 80), ('E5', 80), ('G5', 120), ('C6', 150)
    ],
    
    # Respuesta incorrecta - descendente triste
    'incorrecto': [
        ('G4', 100), ('E4', 100), ('C4', 150), ('G3', 200)
    ],
    
    # Subida de nivel - fanfarria completa
    'level_up': [
        ('C4', 80), ('E4', 80), ('G4', 80),
        ('C5', 80), ('E5', 80), ('G5', 80),
        ('C6', 200),
        ('_', 50),
        ('G5', 80), ('C6', 300)
    ],
    
    # Paciente curado - melodía feliz
    'curado': [
        ('C5', 100), ('D5', 100), ('E5', 100), ('G5', 150),
        ('E5', 100), ('G5', 250)
    ],
    
    # Paciente huye - melodía triste
    'huye': [
        ('E4', 150), ('D4', 150), ('C4', 200),
        ('_', 50),
        ('G3', 300)
    ],
    
    # Nuevo paciente - atención
    'nuevo_paciente': [
        ('G4', 80), ('G4', 80), ('_', 40),
        ('G4', 80), ('C5', 150)
    ],
    
    # Beep simple
    'beep': [
        ('C5', 50)
    ],
    
    # Beep doble
    'beep2': [
        ('C5', 50), ('_', 30), ('C5', 50)
    ],
    
    # Error
    'error': [
        ('C4', 200), ('_', 50), ('C4', 200)
    ],
    
    # Selección de menú
    'click': [
        ('E5', 30)
    ],
    
    # Game over
    'game_over': [
        ('C5', 150), ('G4', 150), ('E4', 150), ('C4', 300),
        ('_', 100),
        ('G3', 150), ('C3', 400)
    ],
    
    # Victoria
    'victoria': [
        ('C4', 100), ('C4', 100), ('C4', 100), ('C4', 300),
        ('G#3', 300), ('A#3', 300),
        ('C4', 100), ('_', 50), ('A#3', 100), ('C4', 400)
    ],
    
    # Boot del sistema
    'boot': [
        ('C4', 50), ('E4', 50), ('G4', 50), ('C5', 100)
    ],
    
    # === SONIDOS DE FARMACOS ===
    
    # Compra en tienda - monedas
    'compra': [
        ('E5', 40), ('G5', 40), ('E5', 40), ('C5', 80)
    ],
    
    # Pastilla/píldora genérica
    'pastilla': [
        ('G4', 60), ('C5', 60), ('E5', 80)
    ],
    
    # Electroshock - zap
    'electroshock': [
        ('C6', 30), ('_', 20), ('C6', 30), ('_', 20),
        ('G5', 50), ('C6', 100)
    ],
    
    # Hipnosis - ondulante
    'hipnosis': [
        ('E4', 80), ('G4', 80), ('E4', 80), ('G4', 80),
        ('A4', 100), ('G4', 150)
    ],
    
    # Lobotomía - inquietante
    'lobotomia': [
        ('C4', 100), ('_', 30), ('C4', 100), ('_', 30),
        ('G3', 200)
    ],
    
    # Suero de la verdad - misterioso
    'suero': [
        ('E5', 60), ('D5', 60), ('C5', 60),
        ('D5', 60), ('E5', 120)
    ],
    
    # Café - energético
    'cafe': [
        ('C5', 40), ('E5', 40), ('G5', 40),
        ('C6', 40), ('G5', 40), ('C6', 80)
    ]
}


class Audio:
    """Controlador de audio 8-bit no-bloqueante"""

    def __init__(self, pin_num):
        """
        Inicializa el sistema de audio.

        Args:
            pin_num: Número de GPIO para el speaker
        """
        self.pin = Pin(pin_num, Pin.OUT)
        self.pwm = None
        self.enabled = True
        self.timer = Timer(0)  # Timer para audio no-bloqueante
        self._queue = []  # Cola de notas a reproducir
        self._playing = False

    def _timer_callback(self, t):
        """Callback del timer para reproducir siguiente nota"""
        # Apagar nota actual
        if self.pwm:
            self.pwm.deinit()
            self.pwm = None

        # Si hay más notas en cola, reproducir siguiente
        if self._queue:
            nota, duracion = self._queue.pop(0)
            freq = NOTAS.get(nota, 0) if isinstance(nota, str) else nota

            if freq > 0:
                self.pwm = PWM(self.pin, freq=freq, duty=512)

            # Programar siguiente callback (+10ms pausa entre notas)
            self.timer.init(mode=Timer.ONE_SHOT, period=duracion + 10,
                           callback=self._timer_callback)
        else:
            self._playing = False

    def play(self, nombre):
        """
        Reproduce una melodía predefinida (no-bloqueante).

        Args:
            nombre: Nombre de la melodía (ver MELODIAS)
        """
        if not self.enabled:
            return

        # Si ya está reproduciendo, detener primero
        if self._playing:
            self.stop()

        melodia = MELODIAS.get(nombre, [])
        if not melodia:
            return

        self._queue = list(melodia)
        self._playing = True

        # Iniciar primera nota
        nota, duracion = self._queue.pop(0)
        freq = NOTAS.get(nota, 0)

        if freq > 0:
            self.pwm = PWM(self.pin, freq=freq, duty=512)

        self.timer.init(mode=Timer.ONE_SHOT, period=duracion + 10,
                       callback=self._timer_callback)

    def play_blocking(self, nombre):
        """
        Reproduce una melodía de forma bloqueante (para compatibilidad).

        Args:
            nombre: Nombre de la melodía (ver MELODIAS)
        """
        if not self.enabled:
            return

        melodia = MELODIAS.get(nombre, [])
        for nota, duracion in melodia:
            freq = NOTAS.get(nota, 0)
            if freq == 0:
                if self.pwm:
                    self.pwm.deinit()
                    self.pwm = None
                time.sleep_ms(duracion)
            else:
                self.pwm = PWM(self.pin, freq=freq, duty=512)
                time.sleep_ms(duracion)
                self.pwm.deinit()
                self.pwm = None
            time.sleep_ms(10)

    def play_custom(self, melodia):
        """
        Reproduce una melodía personalizada (no-bloqueante).

        Args:
            melodia: Lista de tuplas (nota, duracion_ms)
        """
        if not self.enabled:
            return

        if self._playing:
            self.stop()

        self._queue = list(melodia)
        self._playing = True

        if self._queue:
            nota, duracion = self._queue.pop(0)
            freq = NOTAS.get(nota, 0) if isinstance(nota, str) else nota

            if freq > 0:
                self.pwm = PWM(self.pin, freq=freq, duty=512)

            self.timer.init(mode=Timer.ONE_SHOT, period=duracion + 10,
                           callback=self._timer_callback)

    def beep(self, freq=1000, duration=50):
        """Beep simple (no-bloqueante)"""
        if not self.enabled:
            return

        if self._playing:
            self.stop()

        self.pwm = PWM(self.pin, freq=freq, duty=512)
        self._playing = True
        self.timer.init(mode=Timer.ONE_SHOT, period=duration,
                       callback=self._timer_callback)

    def toggle(self):
        """Activa/desactiva el audio"""
        self.enabled = not self.enabled
        if not self.enabled:
            self.stop()
        return self.enabled

    def set_enabled(self, enabled):
        """Establece si el audio está activo"""
        self.enabled = enabled
        if not enabled:
            self.stop()

    def stop(self):
        """Detiene cualquier sonido"""
        self.timer.deinit()
        self._queue = []
        self._playing = False
        if self.pwm:
            self.pwm.deinit()
            self.pwm = None

    def is_playing(self):
        """Retorna True si hay audio reproduciéndose"""
        return self._playing


# Instancia global (se inicializa desde main)
audio = None

def init_audio(pin_num):
    """Inicializa el sistema de audio global"""
    global audio
    audio = Audio(pin_num)
    return audio

def play(nombre):
    """Reproduce una melodía si el audio está inicializado"""
    if audio:
        audio.play(nombre)

def beep(freq=1000, duration=50):
    """Beep simple si el audio está inicializado"""
    if audio:
        audio.beep(freq, duration)
