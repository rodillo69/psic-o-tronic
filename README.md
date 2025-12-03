# 🧠 PSIC-O-TRONIC

> *El simulador de consulta psicológica más absurdo jamás creado*

**PSIC-O-TRONIC** es un juego de simulación con humor negro donde te conviertes en un psicólogo de dudosa ética profesional. Tus pacientes tienen problemas absurdos y tus métodos de tratamiento son... cuestionables.

Desarrollado por **Miguel Cañadas** ([@rodillo69](https://github.com/rodillo69))

---

## 📸 Vista General

```
┌────────────────────┐
│ Dr. Mengele        │  ← Tu nombre profesional
│ 15/03/25   14:32   │  ← Fecha y hora
│ >> 3 MENSAJES <<   │  ← Pacientes esperando
│ Nv12 Charlatán     │  ← Nivel y rango
└────────────────────┘
     [▲] [●] [▼]        ← Controles físicos
```

---

## 🎮 Modos de Juego

### 🎯 Modo Clásico
Partidas rápidas con cuota de pacientes. Cura la cantidad requerida antes de que huyan todos. Ideal para partidas cortas.

### 💀 Modo Survival
¿Cuántos pacientes puedes curar sin fallar? Un error y game over. Para los más temerarios.

### 🏥 Modo Mi Consulta
El modo principal. Gestiona tu propia clínica psicológica:

- **Pacientes persistentes**: Cada paciente tiene nombre, historial, personalidad y múltiples sesiones
- **Economía completa**: Gana dinero, compra fármacos, mejora tu consulta
- **Progresión RPG**: Sube de nivel, desbloquea rangos, consigue logros
- **Eventos diarios**: Cada día trae sorpresas (buenas y malas)
- **Sistema de racha**: Cura pacientes consecutivamente para multiplicadores
- **Misiones**: Objetivos diarios y semanales con recompensas
- **Crafting**: Combina fármacos para crear tratamientos especiales
- **Prestigio**: Reinicia con bonificaciones permanentes

---

## 🛠️ Hardware

### Componentes Necesarios

| Componente | Especificación |
|------------|----------------|
| Microcontrolador | ESP32-S3 (con WiFi) |
| Pantalla | LCD 20x4 I2C (PCF8574) |
| Botones | 3x pulsadores momentáneos |
| LEDs | 4x LEDs (3 botones + notificación) |
| Altavoz | Buzzer pasivo (opcional) |
| Alimentación | USB-C o batería 3.7V |

### Conexiones GPIO

```
ESP32-S3 Pin    Componente
────────────────────────────
GPIO 1  ───────  SDA (LCD)
GPIO 2  ───────  SCL (LCD)
GPIO 4  ───────  Botón UP
GPIO 5  ───────  Botón SELECT
GPIO 6  ───────  Botón DOWN
GPIO 7  ───────  LED UP
GPIO 15 ───────  LED SELECT
GPIO 16 ───────  LED DOWN
GPIO 17 ───────  LED Notificación
GPIO 9  ───────  Altavoz (PWM)
```

### Esquema de Conexión

```
                    ┌─────────────────┐
                    │    ESP32-S3     │
                    │                 │
    ┌───────────────┤ GPIO1 (SDA)     │
    │  ┌────────────┤ GPIO2 (SCL)     │
    │  │            │                 │
    │  │   ┌────────┤ GPIO4           │──── BTN_UP ────┐
    │  │   │  ┌─────┤ GPIO5           │──── BTN_SEL ───┼──── GND
    │  │   │  │  ┌──┤ GPIO6           │──── BTN_DOWN ──┘
    │  │   │  │  │  │                 │
    │  │   │  │  │  ├ GPIO7  ─────────┼──── LED_UP ────┬── 330Ω ── GND
    │  │   │  │  │  ├ GPIO15 ─────────┼──── LED_SEL ───┤
    │  │   │  │  │  ├ GPIO16 ─────────┼──── LED_DOWN ──┤
    │  │   │  │  │  ├ GPIO17 ─────────┼──── LED_NOTIFY ┘
    │  │   │  │  │  │                 │
    │  │   │  │  │  ├ GPIO9  ─────────┼──── BUZZER ──── GND
    │  │   │  │  │  │                 │
    │  │   │  │  │  └─────────────────┘
    │  │   │  │  │
┌───┴──┴───┴──┴──┴───┐
│   LCD 20x4 I2C     │
│   (PCF8574 0x27)   │
└────────────────────┘
```

---

## 📦 Instalación

### 1. Preparar el ESP32-S3

Instala MicroPython en tu ESP32-S3:

```bash
# Descargar firmware de micropython.org
esptool.py --chip esp32s3 erase_flash
esptool.py --chip esp32s3 write_flash -z 0 esp32s3-firmware.bin
```

### 2. Clonar el Repositorio

```bash
git clone https://github.com/rodillo69/psic-o-tronic.git
cd psic-o-tronic
```

### 3. Subir Archivos

Usa `mpremote`, `ampy` o Thonny para copiar todos los archivos `.py` y `version.json`:

```bash
# Con mpremote
mpremote cp *.py :
mpremote cp version.json :

# O con ampy
ampy put main.py
ampy put career_mode.py
# ... (todos los archivos)
```

### 4. Configuración Inicial

Al encender por primera vez:

1. El dispositivo creará un punto de acceso WiFi: **PSIC-O-TRONIC**
2. Conéctate desde tu móvil/PC
3. Abre el navegador en `192.168.4.1`
4. Configura:
   - Tu red WiFi (SSID y contraseña)
   - Tu API Key de Google Gemini

---

## 🔑 API Key de Gemini

El juego utiliza **Google Gemini** para generar las respuestas dinámicas de los pacientes.

### Obtener API Key Gratuita

1. Ve a [Google AI Studio](https://aistudio.google.com/)
2. Inicia sesión con tu cuenta de Google
3. Haz clic en "Get API Key"
4. Crea una nueva API Key
5. Cópiala e introdúcela en el portal de configuración

> ⚠️ La API gratuita tiene límites de uso. Para uso intensivo, considera el plan de pago.

---

## 🎯 Controles

| Botón | Acción |
|-------|--------|
| **▲ UP** | Navegar arriba / Opción anterior |
| **● SELECT** | Confirmar / Seleccionar |
| **▼ DOWN** | Navegar abajo / Opción siguiente |
| **▲ + ▼** | Volver atrás (mantener ambos) |

### LEDs Indicadores

| LED | Significado |
|-----|-------------|
| 🔵 UP | Puedes navegar arriba |
| 🟢 SELECT | Puedes seleccionar |
| 🔵 DOWN | Puedes navegar abajo |
| 🟡 NOTIFY | Nuevo mensaje / Notificación |

---

## 🏥 Sistemas de Juego (Mi Consulta)

### 💊 El Camello (Tienda)

Compra fármacos de dudosa procedencia para "tratar" a tus pacientes:

| Fármaco | Precio | Efecto |
|---------|--------|--------|
| Placebo Premium | 50€ | +10% probabilidad de cura |
| Ansiolítico Genérico | 80€ | Reduce ansiedad del paciente |
| Estimulante Soviet | 120€ | El paciente habla más |
| Suero de la Verdad | 200€ | Revela información oculta |
| *... y más* | | |

### 🔧 Mejoras de Consulta

Invierte en tu clínica:

- **Diploma Falso**: +5% confianza inicial
- **Sofá Ergonómico**: Pacientes aguantan más sesiones
- **Máquina de Café**: Reduce tiempo entre pacientes
- **Ruleta del Loco**: Desbloquea el sistema de apuestas
- **Mesa de Crafting**: Combina fármacos
- *... 15 mejoras en total*

### 🏆 Logros

35 logros en 6 categorías:

- **Curación**: Por curar pacientes
- **Fracaso**: Por perder pacientes (sí, también dan premios)
- **Economía**: Por ganar/gastar dinero
- **Coleccionismo**: Por obtener items
- **Secretos**: Descúbrelos tú mismo...

### 👔 Vestuario

Personaliza tu bata de doctor:

- Bata Clásica (gratis)
- Bata Hawaiana
- Bata de Cuero
- Bata Invisible (???)
- *... 10 opciones*

### ⚗️ Crafting

Combina fármacos para crear tratamientos especiales:

```
Placebo + Estimulante = Efecto Placebo Potenciado
Ansiolítico + Suero = Confesión Tranquila
```

### 🎰 Apuestas

¿Te sientes con suerte? Apuesta tu dinero duramente ganado en la Ruleta del Loco. ¿Qué puede salir mal?

### ⭐ Prestigio

Al llegar al nivel 50, puedes "prestigiar":
- Reinicia tu progreso
- Mantienes bonificaciones permanentes
- Desbloquea contenido exclusivo

---

## 🌐 Portal WiFi

Accede a la configuración completa desde cualquier navegador:

### Características

- **Dashboard**: Estadísticas en tiempo real
- **Configuración WiFi**: Cambia de red, escanea redes disponibles
- **API Key**: Actualiza tu clave de Gemini
- **Mi Consulta**: Ve tu progreso, estadísticas, logros
- **Manual**: Documentación completa del juego
- **Reset**: Borra datos (con confirmación)

### Acceso

1. Desde el menú principal: `WiFi`
2. O cuando no hay WiFi configurado, se activa automáticamente
3. Conéctate a la red `PSIC-O-TRONIC`
4. Abre `192.168.4.1` en tu navegador

---

## 🔄 Actualizaciones OTA

El juego se actualiza automáticamente desde GitHub:

1. Ve a `Menú → Actualizar`
2. El dispositivo verificará si hay nuevas versiones
3. Si hay actualización disponible, confirma la instalación
4. Los archivos se descargan y reemplazan automáticamente
5. Reinicia para aplicar cambios

> Las actualizaciones sobrescriben los archivos del programa, no tus datos de partida.

---

## 📁 Estructura del Proyecto

```
psic-o-tronic/
├── main.py              # Punto de entrada, menú principal
├── career_mode.py       # Motor del modo Mi Consulta
├── career_data.py       # Gestión de datos persistentes
├── career_patients.py   # Generación de pacientes
├── career_systems.py    # Sistemas de juego (tienda, logros, etc.)
├── career_scheduler.py  # Programación de eventos
├── game_modes.py        # Modos Clásico y Survival
├── gemini_api.py        # Integración con Google Gemini
├── wifi_portal.py       # Portal cautivo y configuración web
├── ota_update.py        # Sistema de actualizaciones OTA
├── config.py            # Configuración y persistencia
├── error_handler.py     # Gestión de errores
├── audio.py             # Sistema de sonido
├── ui_renderer.py       # Renderizado de UI
├── lcd_api.py           # Driver LCD base
├── i2c_lcd.py           # Driver LCD I2C
├── lcd_chars.py         # Caracteres personalizados
├── ntp_time.py          # Sincronización de hora
└── version.json         # Versión actual para OTA
```

---

## 🐛 Solución de Problemas

### No conecta al WiFi

1. Verifica que el SSID y contraseña son correctos
2. Asegúrate de que tu red es 2.4GHz (ESP32 no soporta 5GHz)
3. Reinicia el dispositivo

### Error de API

1. Verifica que tu API Key es válida
2. Comprueba que tienes conexión a internet
3. Puede que hayas excedido el límite gratuito de Gemini

### Pantalla en blanco

1. Verifica las conexiones I2C (SDA, SCL)
2. Comprueba la dirección I2C (por defecto 0x27, puede ser 0x3F)
3. Ajusta el contraste con el potenciómetro del módulo LCD

### Los botones no responden

1. Verifica las conexiones GPIO
2. Asegúrate de que los botones están conectados a GND
3. Comprueba que los pines no están dañados

### Reinicio constante

1. Puede ser falta de memoria. Reinicia el dispositivo
2. Verifica la alimentación (mínimo 500mA)
3. Borra los datos desde el portal WiFi y empieza de nuevo

---

## 📊 Especificaciones Técnicas

| Característica | Valor |
|----------------|-------|
| Lenguaje | MicroPython |
| Plataforma | ESP32-S3 |
| RAM mínima | 512KB |
| Flash mínima | 4MB |
| Pantalla | LCD 20x4 caracteres |
| Protocolo LCD | I2C @ 400kHz |
| WiFi | 802.11 b/g/n (2.4GHz) |
| Frecuencia CPU | 240MHz |
| Consumo típico | ~150mA |
| Consumo standby | ~50mA |

---

## 🤝 Contribuir

¿Quieres aportar al proyecto?

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -am 'Añade nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

### Ideas para contribuir

- [ ] Nuevos fármacos y efectos
- [ ] Más tipos de pacientes
- [ ] Eventos especiales
- [ ] Traducciones a otros idiomas
- [ ] Mejoras de UI
- [ ] Nuevos modos de juego

---

## 📜 Licencia

Este proyecto está bajo la Licencia MIT. Ver [LICENSE](LICENSE) para más detalles.

---

## 👤 Autor

**Miguel Cañadas** ([@rodillo69](https://github.com/rodillo69))

- GitHub: [github.com/rodillo69](https://github.com/rodillo69)

---

## ⚠️ Disclaimer

*PSIC-O-TRONIC es un juego de humor negro y sátira. No pretende ser una representación realista de la psicología o la salud mental. Si necesitas ayuda profesional de verdad, consulta a un profesional de salud mental real, no a un ESP32.*

---

<p align="center">
  <i>Hecho con 🧠 y dudosa ética profesional</i>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/pacientes%20curados-42-green" />
  <img src="https://img.shields.io/badge/pacientes%20huidos-∞-red" />
  <img src="https://img.shields.io/badge/demandas%20pendientes-7-yellow" />
</p>
