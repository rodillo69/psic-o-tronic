# lcd_api.py - API base para LCD HD44780
import time

class LcdApi:
    def __init__(self, num_lines, num_columns):
        self.num_lines = num_lines
        self.num_columns = num_columns
        self.cursor_x = 0
        self.cursor_y = 0
        self.implied_newline = False
        self.backlight = True
        self.display_off()
        self.backlight_on()
        self.clear()
        self.entry_mode_set(1, 0)
        self.display_on()

    def clear(self):
        self.hal_write_command(0x01)
        time.sleep_ms(2)
        self.cursor_x = 0
        self.cursor_y = 0

    def move_to(self, cursor_x, cursor_y):
        self.cursor_x = cursor_x
        self.cursor_y = cursor_y
        addr = cursor_x & 0x3f
        if cursor_y & 1:
            addr += 0x40
        if cursor_y & 2:
            addr += 0x14
        self.hal_write_command(0x80 | addr)

    def putchar(self, char):
        if char == '\n':
            if self.implied_newline:
                pass
            else:
                self.cursor_x = 0
                self.cursor_y += 1
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
                self.move_to(self.cursor_x, self.cursor_y)
        else:
            self.hal_write_data(ord(char))
            self.cursor_x += 1
            if self.cursor_x >= self.num_columns:
                self.cursor_x = 0
                self.cursor_y += 1
                self.implied_newline = (char != '\n')
                if self.cursor_y >= self.num_lines:
                    self.cursor_y = 0
                self.move_to(self.cursor_x, self.cursor_y)
            else:
                self.implied_newline = False

    def putstr(self, string):
        for char in string:
            self.putchar(char)

    def custom_char(self, location, charmap):
        """
        Define un carácter custom en CGRAM.
        
        Args:
            location: Posición 0-7
            charmap: bytearray de 8 bytes con el patrón
        """
        location &= 0x7
        self.hal_write_command(0x40 | (location << 3))
        time.sleep_us(40)
        for byte in charmap:
            self.hal_write_data(byte)
            time.sleep_us(40)
        self.move_to(self.cursor_x, self.cursor_y)

    def backlight_on(self):
        self.backlight = True
        self.hal_backlight_on()

    def backlight_off(self):
        self.backlight = False
        self.hal_backlight_off()

    def display_on(self):
        self.hal_write_command(0x0C)

    def display_off(self):
        self.hal_write_command(0x08)

    def entry_mode_set(self, inc, shift):
        flags = 0x04
        if inc:
            flags |= 0x02
        if shift:
            flags |= 0x01
        self.hal_write_command(flags)

    def hal_backlight_on(self):
        pass

    def hal_backlight_off(self):
        pass

    def hal_write_command(self, cmd):
        pass

    def hal_write_data(self, data):
        pass
