# ============================================================================
# GAME_MODES.PY - Modos de Juego
# PSIC-O-TRONIC - Clásico y Survival
# ============================================================================

from config import (
    load_stats, save_stats, record_game_start, record_case_solved,
    check_streak_record, check_survival_record
)

# Tipos de modo
MODE_CLASSIC = "classic"
MODE_SURVIVAL = "survival"


class GameSession:
    """
    Sesión de juego que maneja estado común a todos los modos.
    """
    
    def __init__(self, mode, num_players=1, quota=5):
        """
        Args:
            mode: MODE_CLASSIC o MODE_SURVIVAL
            num_players: Número de jugadores (1-4)
            quota: Casos a resolver (solo clásico)
        """
        self.mode = mode
        self.num_players = num_players
        self.quota = quota if mode == MODE_CLASSIC else 999
        
        # Estado de jugadores
        self.players = []
        self.current_player_idx = 0
        self.lives_max = 3
        
        # Puntuación
        self.total_score = 0
        self.current_streak = 0
        
        # Estado del juego
        self.game_won = False
        self.game_over = False
        
        # Escenario actual
        self.scenario = None
        self.selected_option = 0
        
        # Scroll para lectura
        self.scroll_lines = []
        self.scroll_idx = 0
        
        # Último feedback
        self.last_result_ok = False
        self.last_feedback = ""
        
        # Para récords
        self.initials = "???"
        
        # Registrar inicio de partida
        record_game_start()
    
    def start(self):
        """Inicia la sesión de juego"""
        self.players = [
            {'id': i + 1, 'lives': self.lives_max, 'score': 0}
            for i in range(self.num_players)
        ]
        self.current_player_idx = 0
        self.total_score = 0
        self.current_streak = 0
        self.game_won = False
        self.game_over = False
    
    def get_current_player(self):
        """Obtiene el jugador actual"""
        if self.players:
            return self.players[self.current_player_idx]
        return None
    
    def get_prompt_modifier(self):
        """Obtiene modificador de prompt según el modo"""
        return ""
    
    def process_answer(self, selected_idx):
        """
        Procesa la respuesta del jugador.
        
        Args:
            selected_idx: Índice de opción seleccionada (0-3)
            
        Returns:
            True si acertó, False si falló
        """
        if not self.scenario:
            return False
        
        correct = self.scenario.get('correcta', 0)
        is_correct = (selected_idx == correct)
        
        player = self.get_current_player()
        
        if is_correct:
            # Acierto
            self.last_result_ok = True
            self.last_feedback = self.scenario.get('feedback_win', 'Correcto')
            
            if player:
                player['score'] += 1
            self.total_score += 1
            self.current_streak += 1
            
            # Registrar caso resuelto
            record_case_solved()
        else:
            # Fallo
            self.last_result_ok = False
            self.last_feedback = self.scenario.get('feedback_lose', 'Error')
            
            if player:
                player['lives'] -= 1
            
            # Resetear racha
            self._check_and_save_streak()
            self.current_streak = 0
        
        return is_correct
    
    def _check_and_save_streak(self):
        """Comprueba y guarda récord de racha"""
        if self.current_streak > 0:
            check_streak_record(self.current_streak, self.initials)
    
    def check_game_state(self):
        """
        Comprueba el estado del juego después de una respuesta.
        
        Returns:
            "continue" - Seguir jugando
            "win" - Victoria
            "game_over" - Fin del juego
        """
        # Comprobar victoria por cuota (modo clásico)
        if self.mode == MODE_CLASSIC:
            if self.total_score >= self.quota:
                self.game_won = True
                self._check_and_save_streak()
                return "win"
        
        # Comprobar si hay jugadores vivos
        alive_players = [p for p in self.players if p['lives'] > 0]
        
        if not alive_players:
            self.game_over = True
            self._check_and_save_streak()
            
            # Modo survival: guardar récord
            if self.mode == MODE_SURVIVAL:
                check_survival_record(self.total_score, self.initials)
            
            return "game_over"
        
        return "continue"
    
    def next_turn(self):
        """
        Pasa al siguiente jugador (multiplayer).
        
        Returns:
            True si hay más jugadores, False si no
        """
        if self.num_players <= 1:
            return self.players[0]['lives'] > 0
        
        initial = self.current_player_idx
        while True:
            self.current_player_idx = (self.current_player_idx + 1) % self.num_players
            if self.players[self.current_player_idx]['lives'] > 0:
                return True
            if self.current_player_idx == initial:
                return False
    
    def get_mvp(self):
        """Obtiene el jugador con más puntos"""
        if self.players:
            return max(self.players, key=lambda p: p['score'])
        return None
    
    def get_status_line(self):
        """
        Genera línea de estado para el LCD.
        
        Returns:
            String de 20 caracteres con estado
        """
        player = self.get_current_player()
        if not player:
            return " " * 20
        
        # Formato: P1 ♥♥♡    OBJ:3/5
        lives_display = chr(0) * player['lives'] + chr(1) * (self.lives_max - player['lives'])
        
        if self.mode == MODE_CLASSIC:
            right = f"OBJ:{self.total_score}/{self.quota}"
        else:  # Survival
            right = f"PTS:{self.total_score}"
        
        left = f"P{player['id']} {lives_display}"
        
        spaces = 20 - len(left) - len(right)
        if spaces < 1:
            spaces = 1
        
        return (left + " " * spaces + right)[:20]


class InitialsInput:
    """
    Helper para input de iniciales (3 caracteres).
    """
    
    CHARS = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789 "
    
    def __init__(self):
        self.positions = [0, 0, 0]  # Índice en CHARS para cada posición
        self.current_pos = 0  # Posición actual (0-2)
    
    def up(self):
        """Sube el carácter actual"""
        self.positions[self.current_pos] = (self.positions[self.current_pos] + 1) % len(self.CHARS)
    
    def down(self):
        """Baja el carácter actual"""
        self.positions[self.current_pos] = (self.positions[self.current_pos] - 1) % len(self.CHARS)
    
    def next(self):
        """Avanza a la siguiente posición"""
        if self.current_pos < 2:
            self.current_pos += 1
            return False  # No terminado
        return True  # Terminado
    
    def get_display(self):
        """Obtiene string para mostrar"""
        chars = [self.CHARS[p] for p in self.positions]
        # Marcar posición actual
        result = ""
        for i, c in enumerate(chars):
            if i == self.current_pos:
                result += f"[{c}]"
            else:
                result += f" {c} "
        return result
    
    def get_initials(self):
        """Obtiene las iniciales finales"""
        return "".join([self.CHARS[p] for p in self.positions])


# Test standalone
if __name__ == "__main__":
    print("=== Test Game Modes ===")
    
    # Test sesión clásica
    print("\n--- Modo Clásico ---")
    session = GameSession(MODE_CLASSIC, num_players=2, quota=3)
    session.start()
    
    print(f"Jugadores: {session.players}")
    print(f"Status: {session.get_status_line()}")
    
    # Simular escenario
    session.scenario = {
        "correcta": 0,
        "feedback_win": "Bien hecho",
        "feedback_lose": "Despedido"
    }
    
    # Simular respuestas
    for i in range(5):
        result = session.process_answer(0 if i < 3 else 1)
        state = session.check_game_state()
        print(f"Turno {i+1}: {'OK' if result else 'FAIL'} -> {state}")
        if state != "continue":
            break
        session.next_turn()
    
    # Test survival
    print("\n--- Modo Survival ---")
    survival = GameSession(MODE_SURVIVAL, num_players=1)
    survival.start()
    print(f"Status: {survival.get_status_line()}")
    
    # Test iniciales
    print("\n--- Input Iniciales ---")
    initials = InitialsInput()
    print(f"Display: {initials.get_display()}")
    initials.up()
    initials.up()
    initials.next()
    initials.down()
    initials.next()
    print(f"Display: {initials.get_display()}")
    print(f"Iniciales: {initials.get_initials()}")
