# ============================================================================
# CAREER_SYSTEMS.PY - Sistemas avanzados del modo carrera
# PSIC-O-TRONIC - Logros, Rachas, Mejoras, Eventos
# ============================================================================

import random

# ============================================================================
# LOGROS - 35 logros en 6 categorías
# ============================================================================

LOGROS = {
    # =========================================================================
    # PACIENTES (20 logros)
    # =========================================================================
    "primera_sangre": {
        "nombre": "Primera Sangre",
        "desc": "Cura tu primer paciente",
        "condicion": ("pacientes_curados", ">=", 1),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "medico_cabecera": {
        "nombre": "Medico Cabecera",
        "desc": "Cura 10 pacientes",
        "condicion": ("pacientes_curados", ">=", 10),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "curandero": {
        "nombre": "El Curandero",
        "desc": "Cura 25 pacientes",
        "condicion": ("pacientes_curados", ">=", 25),
        "recompensa": {"dinero": 500},
        "secreto": False
    },
    "dios_psiquiatria": {
        "nombre": "Dios Psiquiatria",
        "desc": "Cura 50 pacientes",
        "condicion": ("pacientes_curados", ">=", 50),
        "recompensa": {"dinero": 1000, "titulo": "Dios"},
        "secreto": False
    },
    "mesias": {
        "nombre": "El Mesias",
        "desc": "Cura 100 pacientes",
        "condicion": ("pacientes_curados", ">=", 100),
        "recompensa": {"dinero": 2500, "titulo": "Mesias"},
        "secreto": False
    },
    "chapuzas": {
        "nombre": "El Chapuzas",
        "desc": "5 pacientes huyen",
        "condicion": ("pacientes_abandonados", ">=", 5),
        "recompensa": {"titulo": "Chapuzas"},
        "secreto": False
    },
    "carnicero": {
        "nombre": "El Carnicero",
        "desc": "15 pacientes huyen",
        "condicion": ("pacientes_abandonados", ">=", 15),
        "recompensa": {"titulo": "Carnicero"},
        "secreto": False
    },
    "genocida": {
        "nombre": "Genocida",
        "desc": "30 pacientes huyen",
        "condicion": ("pacientes_abandonados", ">=", 30),
        "recompensa": {"titulo": "Genocida"},
        "secreto": True
    },
    "angel_muerte": {
        "nombre": "Angel de Muerte",
        "desc": "50 pacientes huyen",
        "condicion": ("pacientes_abandonados", ">=", 50),
        "recompensa": {"titulo": "AngelMuerte", "dinero": 666},
        "secreto": True
    },
    "sin_bajas": {
        "nombre": "Sin Bajas",
        "desc": "Cura 5 seguidos sin huidas",
        "condicion": ("racha_curados", ">=", 5),
        "recompensa": {"dinero": 150},
        "secreto": False
    },
    "racha_10": {
        "nombre": "Diez Seguidos",
        "desc": "Cura 10 seguidos sin huidas",
        "condicion": ("racha_curados", ">=", 10),
        "recompensa": {"dinero": 400, "item": "ansio"},
        "secreto": False
    },
    "caso_dificil": {
        "nombre": "Caso Dificil",
        "desc": "Cura un paciente Agresivo",
        "condicion": ("pacientes_agresivos", ">=", 1),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "domador": {
        "nombre": "El Domador",
        "desc": "Cura 10 Agresivos",
        "condicion": ("pacientes_agresivos", ">=", 10),
        "recompensa": {"dinero": 500, "titulo": "Domador"},
        "secreto": False
    },
    "caza_vips": {
        "nombre": "Caza VIPs",
        "desc": "Cura 5 pacientes VIP",
        "condicion": ("pacientes_vip", ">=", 5),
        "recompensa": {"dinero": 800},
        "secreto": False
    },
    "misterio_resuelto": {
        "nombre": "Caso Resuelto",
        "desc": "Cura paciente Misterioso",
        "condicion": ("pacientes_misteriosos", ">=", 1),
        "recompensa": {"dinero": 500, "item": "suero"},
        "secreto": False
    },
    "influencer_killer": {
        "nombre": "Influencer Killer",
        "desc": "Haz huir a un Influencer",
        "condicion": ("influencers_huidos", ">=", 1),
        "recompensa": {"titulo": "AntiSocial"},
        "secreto": True
    },
    "salvador_morosos": {
        "nombre": "Pro Bono",
        "desc": "Cura 10 Morosos",
        "condicion": ("pacientes_morosos", ">=", 10),
        "recompensa": {"dinero": 200, "titulo": "Benefactor"},
        "secreto": False
    },
    "variedad": {
        "nombre": "Variedad",
        "desc": "Cura cada tipo de paciente",
        "condicion": ("tipos_curados", ">=", 12),
        "recompensa": {"dinero": 1000},
        "secreto": False
    },
    "al_limite": {
        "nombre": "Al Limite",
        "desc": "Cura con progreso en -2",
        "condicion": ("curas_al_limite", ">=", 1),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "milagro": {
        "nombre": "Milagro",
        "desc": "Cura con 10 sesiones seguidas bien",
        "condicion": ("curas_milagrosas", ">=", 1),
        "recompensa": {"dinero": 300, "item": "hipno"},
        "secreto": False
    },

    # =========================================================================
    # SESIONES (20 logros)
    # =========================================================================
    "buen_ojo": {
        "nombre": "Buen Ojo",
        "desc": "10 aciertos totales",
        "condicion": ("sesiones_correctas", ">=", 10),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "ojo_clinico": {
        "nombre": "Ojo Clinico",
        "desc": "50 aciertos totales",
        "condicion": ("sesiones_correctas", ">=", 50),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "infalible": {
        "nombre": "Infalible",
        "desc": "100 aciertos totales",
        "condicion": ("sesiones_correctas", ">=", 100),
        "recompensa": {"dinero": 500},
        "secreto": False
    },
    "maestro": {
        "nombre": "Maestro",
        "desc": "250 aciertos totales",
        "condicion": ("sesiones_correctas", ">=", 250),
        "recompensa": {"dinero": 1000},
        "secreto": False
    },
    "iluminado": {
        "nombre": "Iluminado",
        "desc": "500 aciertos totales",
        "condicion": ("sesiones_correctas", ">=", 500),
        "recompensa": {"dinero": 2000, "titulo": "Iluminado"},
        "secreto": False
    },
    "dr_house": {
        "nombre": "Dr. House",
        "desc": "10 aciertos seguidos",
        "condicion": ("racha_aciertos_max", ">=", 10),
        "recompensa": {"dinero": 200, "item": "electro"},
        "secreto": False
    },
    "mentalista": {
        "nombre": "El Mentalista",
        "desc": "20 aciertos seguidos",
        "condicion": ("racha_aciertos_max", ">=", 20),
        "recompensa": {"dinero": 500, "item": "suero"},
        "secreto": False
    },
    "oraculo": {
        "nombre": "El Oraculo",
        "desc": "30 aciertos seguidos",
        "condicion": ("racha_aciertos_max", ">=", 30),
        "recompensa": {"dinero": 1000, "titulo": "Oraculo"},
        "secreto": False
    },
    "dios_aciertos": {
        "nombre": "Omnisciente",
        "desc": "50 aciertos seguidos",
        "condicion": ("racha_aciertos_max", ">=", 50),
        "recompensa": {"dinero": 2500, "titulo": "Omnisciente"},
        "secreto": True
    },
    "tropiezo": {
        "nombre": "Tropezon",
        "desc": "10 fallos totales",
        "condicion": ("sesiones_incorrectas", ">=", 10),
        "recompensa": {"item": "placebo"},
        "secreto": False
    },
    "mantequilla": {
        "nombre": "Manos Mantequilla",
        "desc": "30 fallos totales",
        "condicion": ("sesiones_incorrectas", ">=", 30),
        "recompensa": {"titulo": "Mantequilla"},
        "secreto": False
    },
    "desastre": {
        "nombre": "Desastre Natural",
        "desc": "50 fallos totales",
        "condicion": ("sesiones_incorrectas", ">=", 50),
        "recompensa": {"titulo": "Desastre"},
        "secreto": False
    },
    "catastrofe": {
        "nombre": "Catastrofe",
        "desc": "100 fallos totales",
        "condicion": ("sesiones_incorrectas", ">=", 100),
        "recompensa": {"titulo": "Catastrofe", "dinero": 100},
        "secreto": True
    },
    "racha_mala": {
        "nombre": "Mala Racha",
        "desc": "5 fallos seguidos",
        "condicion": ("racha_fallos_max", ">=", 5),
        "recompensa": {"item": "cafe"},
        "secreto": False
    },
    "perfeccionista": {
        "nombre": "Perfeccionista",
        "desc": "Cura paciente sin fallar",
        "condicion": ("curas_perfectas", ">=", 1),
        "recompensa": {"dinero": 150},
        "secreto": False
    },
    "serial_perfecto": {
        "nombre": "Serial Perfecto",
        "desc": "5 curas perfectas",
        "condicion": ("curas_perfectas", ">=", 5),
        "recompensa": {"dinero": 500},
        "secreto": False
    },
    "cirujano": {
        "nombre": "Precision Quirurgica",
        "desc": "10 curas perfectas",
        "condicion": ("curas_perfectas", ">=", 10),
        "recompensa": {"dinero": 1000, "titulo": "Cirujano"},
        "secreto": False
    },
    "speedrunner": {
        "nombre": "Speedrunner",
        "desc": "Cura en minimo de sesiones",
        "condicion": ("curas_rapidas", ">=", 1),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "flash": {
        "nombre": "Flash",
        "desc": "10 curas rapidas",
        "condicion": ("curas_rapidas", ">=", 10),
        "recompensa": {"dinero": 400, "titulo": "Flash"},
        "secreto": False
    },
    "equilibrado": {
        "nombre": "Equilibrado",
        "desc": "Mismo num aciertos y fallos",
        "condicion": ("equilibrio", "==", 1),
        "recompensa": {"titulo": "Equilibrado"},
        "secreto": True
    },

    # =========================================================================
    # DINERO (15 logros)
    # =========================================================================
    "primer_sueldo": {
        "nombre": "Primer Sueldo",
        "desc": "Gana 500E total",
        "condicion": ("total_ganado", ">=", 500),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "buen_negocio": {
        "nombre": "Buen Negocio",
        "desc": "Gana 2000E total",
        "condicion": ("total_ganado", ">=", 2000),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "prospero": {
        "nombre": "Prospero",
        "desc": "Gana 5000E total",
        "condicion": ("total_ganado", ">=", 5000),
        "recompensa": {"dinero": 250},
        "secreto": False
    },
    "empresario": {
        "nombre": "Empresario",
        "desc": "Gana 15000E total",
        "condicion": ("total_ganado", ">=", 15000),
        "recompensa": {"dinero": 500},
        "secreto": False
    },
    "magnate": {
        "nombre": "El Magnate",
        "desc": "Acumula 5000E",
        "condicion": ("dinero_max", ">=", 5000),
        "recompensa": {"dinero": 200, "titulo": "Magnate"},
        "secreto": False
    },
    "millonario": {
        "nombre": "Millonario",
        "desc": "Acumula 10000E",
        "condicion": ("dinero_max", ">=", 10000),
        "recompensa": {"titulo": "Millonario"},
        "secreto": False
    },
    "mega_rico": {
        "nombre": "Mega Rico",
        "desc": "Acumula 25000E",
        "condicion": ("dinero_max", ">=", 25000),
        "recompensa": {"titulo": "MegaRico", "dinero": 1000},
        "secreto": False
    },
    "derrochador": {
        "nombre": "Derrochador",
        "desc": "Gasta 1000E en tienda",
        "condicion": ("total_gastado", ">=", 1000),
        "recompensa": {"descuento": 5},
        "secreto": False
    },
    "buen_cliente": {
        "nombre": "Buen Cliente",
        "desc": "Gasta 3000E en tienda",
        "condicion": ("total_gastado", ">=", 3000),
        "recompensa": {"descuento": 10},
        "secreto": False
    },
    "vip_camello": {
        "nombre": "VIP del Camello",
        "desc": "Gasta 5000E en tienda",
        "condicion": ("total_gastado", ">=", 5000),
        "recompensa": {"descuento": 15},
        "secreto": False
    },
    "socio_camello": {
        "nombre": "Socio Camello",
        "desc": "Gasta 10000E en tienda",
        "condicion": ("total_gastado", ">=", 10000),
        "recompensa": {"descuento": 20, "titulo": "Socio"},
        "secreto": False
    },
    "tacano": {
        "nombre": "Tacano",
        "desc": "Acumula 2000E sin gastar",
        "condicion": ("tacano", ">=", 1),
        "recompensa": {"titulo": "Tacano"},
        "secreto": True
    },
    "de_cero": {
        "nombre": "De Cero a Heroe",
        "desc": "Llega a 0E y vuelve a 1000E",
        "condicion": ("de_cero", ">=", 1),
        "recompensa": {"dinero": 200},
        "secreto": True
    },
    "ludopata": {
        "nombre": "Ludopata",
        "desc": "Gasta todo tu dinero de golpe",
        "condicion": ("bancarrota", ">=", 3),
        "recompensa": {"titulo": "Ludopata"},
        "secreto": True
    },
    "propinas": {
        "nombre": "Rey Propinas",
        "desc": "Gana 500E en propinas",
        "condicion": ("propinas_total", ">=", 500),
        "recompensa": {"dinero": 100},
        "secreto": False
    },

    # =========================================================================
    # FARMACOS (20 logros)
    # =========================================================================
    "primera_dosis": {
        "nombre": "Primera Dosis",
        "desc": "Usa tu primer farmaco",
        "condicion": ("farmacos_usados", ">=", 1),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "bata_manchada": {
        "nombre": "Bata Manchada",
        "desc": "Usa 10 farmacos",
        "condicion": ("farmacos_usados", ">=", 10),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "farmaceutico": {
        "nombre": "Farmaceutico",
        "desc": "Usa 25 farmacos",
        "condicion": ("farmacos_usados", ">=", 25),
        "recompensa": {"item": "ansio"},
        "secreto": False
    },
    "dr_escobar": {
        "nombre": "Dr. Escobar",
        "desc": "Usa 50 farmacos",
        "condicion": ("farmacos_usados", ">=", 50),
        "recompensa": {"titulo": "Escobar", "item": "lobo"},
        "secreto": False
    },
    "narco": {
        "nombre": "El Narco",
        "desc": "Usa 100 farmacos",
        "condicion": ("farmacos_usados", ">=", 100),
        "recompensa": {"titulo": "Narco", "dinero": 1000},
        "secreto": False
    },
    "sin_escrupulos": {
        "nombre": "Sin Escrupulos",
        "desc": "Usa Suero 5 veces",
        "condicion": ("suero_usado", ">=", 5),
        "recompensa": {"item": "placebo"},
        "secreto": False
    },
    "inquisidor": {
        "nombre": "Inquisidor",
        "desc": "Usa Suero 20 veces",
        "condicion": ("suero_usado", ">=", 20),
        "recompensa": {"titulo": "Inquisidor", "dinero": 500},
        "secreto": False
    },
    "camisa_oro": {
        "nombre": "Camisa de Oro",
        "desc": "Usa Camisa de Fuerza",
        "condicion": ("camisa_usada", ">=", 1),
        "recompensa": {"titulo": "CamisaOro"},
        "secreto": False
    },
    "coleccionista": {
        "nombre": "Coleccionista",
        "desc": "Usa cada tipo de farmaco",
        "condicion": ("tipos_farmacos", ">=", 9),
        "recompensa": {"dinero": 300},
        "secreto": False
    },
    "placebo_master": {
        "nombre": "Placebo Master",
        "desc": "10 placebos que funcionan",
        "condicion": ("placebos_exito", ">=", 10),
        "recompensa": {"dinero": 200, "item": "placebo"},
        "secreto": False
    },
    "placebo_fail": {
        "nombre": "Mala Suerte",
        "desc": "5 placebos fallan seguidos",
        "condicion": ("placebos_fail_racha", ">=", 5),
        "recompensa": {"item": "ansio"},
        "secreto": True
    },
    "electroadicto": {
        "nombre": "Electroadicto",
        "desc": "Usa 15 Electroshocks",
        "condicion": ("electro_usado", ">=", 15),
        "recompensa": {"titulo": "Voltio", "dinero": 200},
        "secreto": False
    },
    "lobotomista": {
        "nombre": "Lobotomista",
        "desc": "Usa 10 Lobotomias",
        "condicion": ("lobo_usado", ">=", 10),
        "recompensa": {"titulo": "Lobotomista"},
        "secreto": False
    },
    "cafeinomano": {
        "nombre": "Cafeinomano",
        "desc": "Usa 20 Cafes del Jefe",
        "condicion": ("cafe_usado", ">=", 20),
        "recompensa": {"dinero": 150, "item": "cafe"},
        "secreto": False
    },
    "hipnotizador": {
        "nombre": "Hipnotizador",
        "desc": "Usa 15 Hipnosis",
        "condicion": ("hipno_usado", ">=", 15),
        "recompensa": {"titulo": "Hipnotista"},
        "secreto": False
    },
    "amnesia": {
        "nombre": "Amnesia Total",
        "desc": "Usa 10 Pastillas Olvido",
        "condicion": ("olvido_usado", ">=", 10),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "combo_drogas": {
        "nombre": "Combo Letal",
        "desc": "Usa 3 farmacos en 1 paciente",
        "condicion": ("combo_farmacos", ">=", 1),
        "recompensa": {"dinero": 250},
        "secreto": False
    },
    "abstinencia": {
        "nombre": "Abstinencia",
        "desc": "Cura 10 sin usar farmacos",
        "condicion": ("curas_sin_drogas", ">=", 10),
        "recompensa": {"dinero": 400, "titulo": "Limpio"},
        "secreto": False
    },
    "inventario_lleno": {
        "nombre": "Acaparador",
        "desc": "Llena el inventario",
        "condicion": ("inventario_lleno", ">=", 1),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "farmacia_andante": {
        "nombre": "Farmacia Andante",
        "desc": "Compra 50 farmacos total",
        "condicion": ("farmacos_comprados", ">=", 50),
        "recompensa": {"descuento": 5},
        "secreto": False
    },

    # =========================================================================
    # PROGRESO Y NIVELES (10 logros)
    # =========================================================================
    "novato": {
        "nombre": "Novato",
        "desc": "Alcanza nivel 5",
        "condicion": ("nivel", ">=", 5),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "aprendiz": {
        "nombre": "Aprendiz",
        "desc": "Alcanza nivel 8",
        "condicion": ("nivel", ">=", 8),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "veterano": {
        "nombre": "Veterano",
        "desc": "Alcanza nivel 10",
        "condicion": ("nivel", ">=", 10),
        "recompensa": {"dinero": 300},
        "secreto": False
    },
    "experto": {
        "nombre": "Experto",
        "desc": "Alcanza nivel 15",
        "condicion": ("nivel", ">=", 15),
        "recompensa": {"dinero": 500, "item": "electro"},
        "secreto": False
    },
    "leyenda": {
        "nombre": "Leyenda",
        "desc": "Alcanza nivel 20",
        "condicion": ("nivel", ">=", 20),
        "recompensa": {"dinero": 1000, "titulo": "Leyenda"},
        "secreto": False
    },
    "mito": {
        "nombre": "El Mito",
        "desc": "Alcanza nivel 30",
        "condicion": ("nivel", ">=", 30),
        "recompensa": {"dinero": 2000, "titulo": "Mito"},
        "secreto": False
    },
    "inmortal": {
        "nombre": "Inmortal",
        "desc": "Alcanza nivel 50",
        "condicion": ("nivel", ">=", 50),
        "recompensa": {"dinero": 5000, "titulo": "Inmortal"},
        "secreto": True
    },
    "dias_jugados_10": {
        "nombre": "Habitual",
        "desc": "Juega 10 dias diferentes",
        "condicion": ("dias_jugados", ">=", 10),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "dias_jugados_30": {
        "nombre": "Adicto",
        "desc": "Juega 30 dias diferentes",
        "condicion": ("dias_jugados", ">=", 30),
        "recompensa": {"dinero": 500, "titulo": "Adicto"},
        "secreto": False
    },
    "veterania": {
        "nombre": "Veterania",
        "desc": "Juega 100 dias diferentes",
        "condicion": ("dias_jugados", ">=", 100),
        "recompensa": {"dinero": 1500, "titulo": "Veterano"},
        "secreto": False
    },

    # =========================================================================
    # ESPECIALES Y SECRETOS (15 logros)
    # =========================================================================
    "primer_evento": {
        "nombre": "Sorpresa!",
        "desc": "Experimenta tu primer evento",
        "condicion": ("eventos_vistos", ">=", 1),
        "recompensa": {"dinero": 30},
        "secreto": False
    },
    "evento_bueno": {
        "nombre": "Dia de Suerte",
        "desc": "10 eventos buenos",
        "condicion": ("eventos_buenos", ">=", 10),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "evento_malo": {
        "nombre": "Mala Estrella",
        "desc": "10 eventos malos",
        "condicion": ("eventos_malos", ">=", 10),
        "recompensa": {"item": "hipno"},
        "secreto": False
    },
    "superviviente": {
        "nombre": "Superviviente",
        "desc": "Sobrevive a inspeccion",
        "condicion": ("inspecciones_pasadas", ">=", 1),
        "recompensa": {"dinero": 100},
        "secreto": False
    },
    "multado": {
        "nombre": "Multado",
        "desc": "Te pillan en inspeccion",
        "condicion": ("inspecciones_falladas", ">=", 1),
        "recompensa": {"titulo": "Sospechoso"},
        "secreto": False
    },
    "mejora_1": {
        "nombre": "Decorador",
        "desc": "Compra tu primera mejora",
        "condicion": ("mejoras_compradas", ">=", 1),
        "recompensa": {"dinero": 50},
        "secreto": False
    },
    "mejora_5": {
        "nombre": "Inversor",
        "desc": "Compra 5 mejoras",
        "condicion": ("mejoras_compradas", ">=", 5),
        "recompensa": {"dinero": 200},
        "secreto": False
    },
    "mejora_todas": {
        "nombre": "Consulta Premium",
        "desc": "Compra todas las mejoras",
        "condicion": ("mejoras_compradas", ">=", 15),
        "recompensa": {"dinero": 1000, "titulo": "Premium"},
        "secreto": False
    },
    "nocturno": {
        "nombre": "Nocturno",
        "desc": "Completa guardia nocturna",
        "condicion": ("guardias_completadas", ">=", 1),
        "recompensa": {"dinero": 150},
        "secreto": False
    },
    "vampiro": {
        "nombre": "Vampiro",
        "desc": "10 guardias nocturnas",
        "condicion": ("guardias_completadas", ">=", 10),
        "recompensa": {"titulo": "Vampiro", "dinero": 500},
        "secreto": False
    },
    "eclipse_total": {
        "nombre": "Eclipse Total",
        "desc": "Sobrevive a dia Eclipse",
        "condicion": ("eclipses_sobrevividos", ">=", 1),
        "recompensa": {"dinero": 300},
        "secreto": True
    },
    "todo_al_reves": {
        "nombre": "Todo Al Reves",
        "desc": "Gana dinero en Eclipse",
        "condicion": ("dinero_eclipse", ">=", 500),
        "recompensa": {"item": "suero"},
        "secreto": True
    },
    "huevo_pascua": {
        "nombre": "???",
        "desc": "???",
        "condicion": ("easter_egg", ">=", 1),
        "recompensa": {"dinero": 999, "titulo": "???"},
        "secreto": True
    },
    "completista": {
        "nombre": "Completista",
        "desc": "Desbloquea 50 logros",
        "condicion": ("logros_desbloqueados", ">=", 50),
        "recompensa": {"dinero": 2000, "titulo": "100%"},
        "secreto": False
    },
    "todo_logros": {
        "nombre": "Platino",
        "desc": "Todos los logros no secretos",
        "condicion": ("logros_no_secretos", ">=", 70),
        "recompensa": {"dinero": 5000, "titulo": "Platino"},
        "secreto": True
    },
}


# ============================================================================
# MEJORAS DE CONSULTA - 15 upgrades permanentes
# ============================================================================

MEJORAS = {
    # =========================================================================
    # DECORACION (8 mejoras)
    # =========================================================================
    "sofa_cuero": {
        "nombre": "Sofa de Cuero",
        "desc": "+10E por sesion",
        "precio": 500,
        "efecto": {"bonus_sesion": 10},
        "requisito": None,
        "categoria": "decoracion"
    },
    "planta_bonita": {
        "nombre": "Planta Bonita",
        "desc": "Pacientes +1 tolerancia",
        "precio": 300,
        "efecto": {"tolerancia_extra": 1},
        "requisito": None,
        "categoria": "decoracion"
    },
    "diploma_falso": {
        "nombre": "Diploma Falso",
        "desc": "+10% XP",
        "precio": 800,
        "efecto": {"xp_mult": 1.1},
        "requisito": None,
        "categoria": "decoracion"
    },
    "cuadro_freud": {
        "nombre": "Cuadro de Freud",
        "desc": "+5% chance VIP",
        "precio": 600,
        "efecto": {"vip_chance": 0.05},
        "requisito": None,
        "categoria": "decoracion"
    },
    "alfombra_persa": {
        "nombre": "Alfombra Persa",
        "desc": "+5% dinero pacientes",
        "precio": 700,
        "efecto": {"dinero_mult": 1.05},
        "requisito": None,
        "categoria": "decoracion"
    },
    "lampara_lava": {
        "nombre": "Lampara de Lava",
        "desc": "Hipnosis dura 2 sesiones",
        "precio": 550,
        "efecto": {"hipnosis_duracion": 2},
        "requisito": None,
        "categoria": "decoracion"
    },
    "pecera": {
        "nombre": "Pecera Relajante",
        "desc": "-10% chance de huida",
        "precio": 650,
        "efecto": {"reduce_huida": 0.1},
        "requisito": "planta_bonita",
        "categoria": "decoracion"
    },
    "divan_premium": {
        "nombre": "Divan Premium",
        "desc": "-1 sesion para curar",
        "precio": 1500,
        "efecto": {"reduce_sesiones": 1},
        "requisito": "sofa_cuero",
        "categoria": "decoracion"
    },
    
    # =========================================================================
    # EQUIPAMIENTO (10 mejoras)
    # =========================================================================
    "maquina_cafe": {
        "nombre": "Maquina de Cafe",
        "desc": "+1 paciente diario max",
        "precio": 400,
        "efecto": {"max_pacientes_dia": 1},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "archivo_secreto": {
        "nombre": "Archivo Secreto",
        "desc": "Ve tipo de paciente",
        "precio": 350,
        "efecto": {"ver_tipo": True},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "telefono_rojo": {
        "nombre": "Telefono Rojo",
        "desc": "Emergencias pagan x2",
        "precio": 900,
        "efecto": {"emergencia_mult": 2},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "caja_fuerte": {
        "nombre": "Caja Fuerte",
        "desc": "No pierdes dinero si huyen",
        "precio": 1200,
        "efecto": {"protege_huida": True},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "nevera": {
        "nombre": "Mini Nevera",
        "desc": "+2 slots inventario",
        "precio": 800,
        "efecto": {"inventario_extra": 2},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "ordenador": {
        "nombre": "Ordenador Antiguo",
        "desc": "Ve stats de paciente",
        "precio": 750,
        "efecto": {"ver_historial": True},
        "requisito": "archivo_secreto",
        "categoria": "equipamiento"
    },
    "impresora": {
        "nombre": "Impresora 3D",
        "desc": "Farmacos +10% efectividad",
        "precio": 1100,
        "efecto": {"farmaco_boost": 0.1},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "aire_acond": {
        "nombre": "Aire Acondicionado",
        "desc": "Eventos malos -20% chance",
        "precio": 950,
        "efecto": {"reduce_malo": 0.2},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "alarma": {
        "nombre": "Sistema Alarma",
        "desc": "Inmune a evento Robo",
        "precio": 600,
        "efecto": {"inmune_robo": True},
        "requisito": None,
        "categoria": "equipamiento"
    },
    "cafetera_pro": {
        "nombre": "Cafetera Italiana",
        "desc": "Cafe del Jefe x2 duracion",
        "precio": 500,
        "efecto": {"cafe_duracion": 2},
        "requisito": "maquina_cafe",
        "categoria": "equipamiento"
    },
    
    # =========================================================================
    # PERSONAL (7 mejoras)
    # =========================================================================
    "secretaria": {
        "nombre": "Secretaria",
        "desc": "Aviso de VIPs",
        "precio": 1000,
        "efecto": {"aviso_vip": True},
        "requisito": None,
        "categoria": "personal"
    },
    "enfermero": {
        "nombre": "Enfermero Turbio",
        "desc": "Placebos +20% exito",
        "precio": 1100,
        "efecto": {"placebo_boost": 0.2},
        "requisito": None,
        "categoria": "personal"
    },
    "seguridad": {
        "nombre": "Seguridad Privada",
        "desc": "Pacientes no huyen 1er fallo",
        "precio": 1400,
        "efecto": {"primer_fallo_gratis": True},
        "requisito": None,
        "categoria": "personal"
    },
    "limpiadora": {
        "nombre": "Limpiadora",
        "desc": "+5% a todo",
        "precio": 800,
        "efecto": {"bonus_global": 0.05},
        "requisito": None,
        "categoria": "personal"
    },
    "recepcionista": {
        "nombre": "Recepcionista",
        "desc": "+10% chance paciente extra",
        "precio": 900,
        "efecto": {"paciente_extra_chance": 0.1},
        "requisito": "secretaria",
        "categoria": "personal"
    },
    "abogado": {
        "nombre": "Abogado",
        "desc": "Multas -50%",
        "precio": 1300,
        "efecto": {"reduce_multa": 0.5},
        "requisito": None,
        "categoria": "personal"
    },
    "hacker": {
        "nombre": "Hacker Amigo",
        "desc": "Inspecciones siempre OK",
        "precio": 2000,
        "efecto": {"inmune_inspeccion": True},
        "requisito": "abogado",
        "categoria": "personal"
    },
    
    # =========================================================================
    # CONEXIONES (5 mejoras)
    # =========================================================================
    "conexion_camello": {
        "nombre": "Conexion Camello",
        "desc": "-15% precio farmacos",
        "precio": 1000,
        "efecto": {"descuento_tienda": 15},
        "requisito": None,
        "categoria": "conexiones"
    },
    "licencia_b": {
        "nombre": "Licencia Clase B",
        "desc": "Desbloquea farmacos raros",
        "precio": 2000,
        "efecto": {"farmacos_raros": True},
        "requisito": "conexion_camello",
        "categoria": "conexiones"
    },
    "contacto_hospital": {
        "nombre": "Contacto Hospital",
        "desc": "Pacientes graves pagan x1.5",
        "precio": 1200,
        "efecto": {"grave_mult": 1.5},
        "requisito": None,
        "categoria": "conexiones"
    },
    "red_morosos": {
        "nombre": "Red de Morosos",
        "desc": "Morosos pagan 50%",
        "precio": 850,
        "efecto": {"moroso_paga": 0.5},
        "requisito": None,
        "categoria": "conexiones"
    },
    "mafia": {
        "nombre": "Contacto Mafia",
        "desc": "Pacientes no huyen nunca",
        "precio": 3000,
        "efecto": {"no_huyen": True},
        "requisito": "seguridad",
        "categoria": "conexiones"
    },
    
    # =========================================================================
    # ESPECIALES (3 mejoras)
    # =========================================================================
    "mesa_crafting": {
        "nombre": "Mesa Crafting",
        "desc": "Combina farmacos",
        "precio": 1500,
        "efecto": {"crafteo": True},
        "requisito": "licencia_b",
        "categoria": "especial"
    },
    "ruleta": {
        "nombre": "Ruleta del Loco",
        "desc": "Desbloquea apuestas",
        "precio": 1000,
        "efecto": {"apuestas": True},
        "requisito": None,
        "categoria": "especial"
    },
    "album_familia": {
        "nombre": "Album Familiar",
        "desc": "Desbloquea casos familiares",
        "precio": 1200,
        "efecto": {"casos_familiares": True},
        "requisito": None,
        "categoria": "especial"
    },
}


# ============================================================================
# PACIENTES ESPECIALES - 12 tipos
# ============================================================================

TIPOS_PACIENTE = {
    # =========================================================================
    # COMUNES (probabilidad total ~60%)
    # =========================================================================
    "normal": {
        "nombre": "Normal",
        "probabilidad": 0.35,
        "modificadores": {},
        "descripcion": "Paciente comun",
        "icono": " "
    },
    "hipocondriaco": {
        "nombre": "Hipocondriaco",
        "probabilidad": 0.10,
        "modificadores": {
            "sesiones_mult": 1.5,
            "dificultad": -1,
            "dinero_mult": 1.0
        },
        "descripcion": "Muchas sesiones faciles",
        "icono": "+"
    },
    "ansioso": {
        "nombre": "Ansioso",
        "probabilidad": 0.08,
        "modificadores": {
            "sesiones_mult": 1.2,
            "mensajes_rapidos": True,
            "dinero_mult": 1.1
        },
        "descripcion": "Mensajes llegan rapido",
        "icono": "!"
    },
    "depresivo": {
        "nombre": "Depresivo",
        "probabilidad": 0.07,
        "modificadores": {
            "sesiones_mult": 1.3,
            "tolerancia": 1,
            "dinero_mult": 0.9
        },
        "descripcion": "Aguanta mas, paga menos",
        "icono": "~"
    },
    
    # =========================================================================
    # DIFICILES (probabilidad total ~15%)
    # =========================================================================
    "agresivo": {
        "nombre": "Agresivo",
        "probabilidad": 0.05,
        "modificadores": {
            "sesiones_mult": 0.7,
            "dificultad": 2,
            "dinero_mult": 2.0,
            "tolerancia": -1
        },
        "descripcion": "Dificil pero paga x2",
        "icono": "X"
    },
    "paranoico": {
        "nombre": "Paranoico",
        "probabilidad": 0.04,
        "modificadores": {
            "opciones_extra": 1,
            "dinero_mult": 1.3,
            "dificultad": 1
        },
        "descripcion": "5 opciones en vez de 4",
        "icono": "?"
    },
    "bipolar": {
        "nombre": "Bipolar",
        "probabilidad": 0.03,
        "modificadores": {
            "aleatorio": True,
            "dinero_mult": 1.5
        },
        "descripcion": "Respuestas cambian",
        "icono": "%"
    },
    "narcisista": {
        "nombre": "Narcisista",
        "probabilidad": 0.03,
        "modificadores": {
            "tolerancia": -2,
            "dinero_mult": 2.5,
            "dificultad": 1
        },
        "descripcion": "Muy exigente, paga bien",
        "icono": "*"
    },
    
    # =========================================================================
    # ECONOMICOS (probabilidad total ~10%)
    # =========================================================================
    "moroso": {
        "nombre": "Moroso",
        "probabilidad": 0.05,
        "modificadores": {
            "dinero_mult": 0.0,
            "xp_mult": 1.5
        },
        "descripcion": "No paga pero +50% XP",
        "icono": "$"
    },
    "vip": {
        "nombre": "VIP",
        "probabilidad": 0.03,
        "modificadores": {
            "dinero_mult": 3.0,
            "tolerancia": -1,
            "dificultad": 1
        },
        "descripcion": "Paga x3 pero exigente",
        "icono": "V"
    },
    "millonario": {
        "nombre": "Millonario",
        "probabilidad": 0.01,
        "modificadores": {
            "dinero_mult": 5.0,
            "tolerancia": -2,
            "propina": 100
        },
        "descripcion": "Paga x5 + propina",
        "icono": "M"
    },
    "estafador": {
        "nombre": "Estafador",
        "probabilidad": 0.01,
        "modificadores": {
            "dinero_mult": -0.5,
            "xp_mult": 2.0,
            "dificultad": 2
        },
        "descripcion": "Te roba dinero!",
        "icono": "#"
    },
    
    # =========================================================================
    # ESPECIALES (probabilidad total ~10%)
    # =========================================================================
    "influencer": {
        "nombre": "Influencer",
        "probabilidad": 0.04,
        "modificadores": {
            "trae_pacientes": 2,
            "dificultad": 1
        },
        "descripcion": "Si curas, trae 2 mas",
        "icono": "@"
    },
    "recurrente": {
        "nombre": "Recurrente",
        "probabilidad": 0.03,
        "modificadores": {
            "vuelve": True,
            "dinero_mult": 0.8
        },
        "descripcion": "Vuelve tras curarse",
        "icono": "R"
    },
    "silencioso": {
        "nombre": "Silencioso",
        "probabilidad": 0.02,
        "modificadores": {
            "mensaje_corto": True,
            "dinero_mult": 1.2
        },
        "descripcion": "Mensajes muy cortos",
        "icono": "."
    },
    "mentiroso": {
        "nombre": "Mentiroso",
        "probabilidad": 0.02,
        "modificadores": {
            "feedback_invertido": True,
            "dinero_mult": 1.5
        },
        "descripcion": "Feedback engañoso",
        "icono": "L"
    },
    "filosofo": {
        "nombre": "Filosofo",
        "probabilidad": 0.02,
        "modificadores": {
            "preguntas_raras": True,
            "xp_mult": 1.5,
            "dinero_mult": 0.8
        },
        "descripcion": "Preguntas existenciales",
        "icono": "F"
    },
    
    # =========================================================================
    # URGENTES (probabilidad total ~3%)
    # =========================================================================
    "urgente": {
        "nombre": "Urgente",
        "probabilidad": 0.02,
        "modificadores": {
            "tiempo_limite": 30,
            "dinero_mult": 2.5
        },
        "descripcion": "30 seg para responder",
        "icono": "U"
    },
    "emergencia": {
        "nombre": "Emergencia",
        "probabilidad": 0.01,
        "modificadores": {
            "tiempo_limite": 15,
            "dinero_mult": 4.0,
            "sesiones_mult": 0.5
        },
        "descripcion": "15 seg! Paga x4",
        "icono": "E"
    },
    
    # =========================================================================
    # RAROS (probabilidad total ~2%)
    # =========================================================================
    "misterioso": {
        "nombre": "???",
        "probabilidad": 0.008,
        "modificadores": {
            "sin_info": True,
            "dinero_mult": 5.0,
            "xp_mult": 3.0
        },
        "descripcion": "Sin datos, x5 todo",
        "icono": "?"
    },
    "fantasma": {
        "nombre": "Fantasma",
        "probabilidad": 0.005,
        "modificadores": {
            "desaparece": True,
            "dinero_mult": 0.0,
            "xp_mult": 5.0
        },
        "descripcion": "Puede desaparecer",
        "icono": "G"
    },
    "celebridad": {
        "nombre": "Celebridad",
        "probabilidad": 0.004,
        "modificadores": {
            "dinero_mult": 10.0,
            "tolerancia": -2,
            "fama": True
        },
        "descripcion": "x10 dinero, muy dificil",
        "icono": "C"
    },
    "gemelos": {
        "nombre": "Gemelos",
        "probabilidad": 0.003,
        "modificadores": {
            "doble": True,
            "dinero_mult": 2.0,
            "sesiones_mult": 2.0
        },
        "descripcion": "2x1, doble de todo",
        "icono": "="
    },
    
    # =========================================================================
    # LEGENDARIOS (probabilidad total <1%)
    # =========================================================================
    "poseido": {
        "nombre": "Poseido",
        "probabilidad": 0.002,
        "modificadores": {
            "respuestas_invertidas": True,
            "dinero_mult": 6.0,
            "xp_mult": 4.0
        },
        "descripcion": "Correcta es incorrecta!",
        "icono": "D"
    },
    "robot": {
        "nombre": "Robot",
        "probabilidad": 0.001,
        "modificadores": {
            "sin_emociones": True,
            "dinero_mult": 8.0,
            "patron_fijo": True
        },
        "descripcion": "Patron predecible",
        "icono": "0"
    },
    "tu_yo": {
        "nombre": "Tu Otro Yo",
        "probabilidad": 0.001,
        "modificadores": {
            "espejo": True,
            "dinero_mult": 0.0,
            "xp_mult": 10.0
        },
        "descripcion": "Te trata a ti mismo",
        "icono": "&"
    },
}


# ============================================================================
# EVENTOS DIARIOS - 25 eventos
# ============================================================================

EVENTOS = {
    # =========================================================================
    # EVENTOS BUENOS (18 eventos)
    # =========================================================================
    "dia_paga": {
        "nombre": "Dia de Paga",
        "desc": "+20% dinero hoy",
        "tipo": "bueno",
        "efecto": {"dinero_mult": 1.2},
        "probabilidad": 0.06
    },
    "rebajas_camello": {
        "nombre": "Rebajas Camello",
        "desc": "-30% en tienda hoy",
        "tipo": "bueno",
        "efecto": {"descuento_dia": 30},
        "probabilidad": 0.05
    },
    "pacientes_generosos": {
        "nombre": "Generosidad",
        "desc": "Pacientes dan 20E propina",
        "tipo": "bueno",
        "efecto": {"propina": 20},
        "probabilidad": 0.06
    },
    "inspiracion": {
        "nombre": "Inspiracion",
        "desc": "+50% XP hoy",
        "tipo": "bueno",
        "efecto": {"xp_mult": 1.5},
        "probabilidad": 0.04
    },
    "cafe_gratis": {
        "nombre": "Cafe Gratis",
        "desc": "Primer acierto = doble XP",
        "tipo": "bueno",
        "efecto": {"primer_doble": True},
        "probabilidad": 0.06
    },
    "buena_racha": {
        "nombre": "Buena Racha",
        "desc": "Empiezas con x1.5 racha",
        "tipo": "bueno",
        "efecto": {"racha_inicial": 1.5},
        "probabilidad": 0.04
    },
    "paciente_agradecido": {
        "nombre": "Agradecimiento",
        "desc": "Ex-paciente te da 100E",
        "tipo": "bueno",
        "efecto": {"dinero_bonus": 100},
        "probabilidad": 0.03
    },
    "envio_camello": {
        "nombre": "Envio Gratis",
        "desc": "Farmaco aleatorio gratis",
        "tipo": "bueno",
        "efecto": {"item_gratis": True},
        "probabilidad": 0.02
    },
    "dia_suerte": {
        "nombre": "Dia de Suerte",
        "desc": "Placebos 100% exito",
        "tipo": "bueno",
        "efecto": {"placebo_seguro": True},
        "probabilidad": 0.03
    },
    "fama_local": {
        "nombre": "Fama Local",
        "desc": "+2 pacientes hoy",
        "tipo": "bueno",
        "efecto": {"pacientes_extra": 2},
        "probabilidad": 0.04
    },
    "luna_llena": {
        "nombre": "Luna Llena",
        "desc": "Pacientes mas locos = +XP",
        "tipo": "bueno",
        "efecto": {"xp_mult": 1.3, "dificultad_extra": 1},
        "probabilidad": 0.03
    },
    "buen_humor": {
        "nombre": "Buen Humor",
        "desc": "Pacientes +1 tolerancia",
        "tipo": "bueno",
        "efecto": {"tolerancia_bonus": 1},
        "probabilidad": 0.04
    },
    "doble_o_nada": {
        "nombre": "Doble o Nada",
        "desc": "Aciertos = x2, Fallos = x2",
        "tipo": "bueno",
        "efecto": {"doble_todo": True},
        "probabilidad": 0.02
    },
    "liquidacion": {
        "nombre": "Liquidacion",
        "desc": "Mejoras -20% hoy",
        "tipo": "bueno",
        "efecto": {"descuento_mejoras": 20},
        "probabilidad": 0.03
    },
    "energia": {
        "nombre": "Energia Extra",
        "desc": "+3 pacientes max hoy",
        "tipo": "bueno",
        "efecto": {"max_pacientes": 3},
        "probabilidad": 0.02
    },
    "herencia": {
        "nombre": "Herencia",
        "desc": "Recibes 200E",
        "tipo": "bueno",
        "efecto": {"dinero_bonus": 200},
        "probabilidad": 0.02
    },
    "critica_buena": {
        "nombre": "Buena Critica",
        "desc": "+10% chance VIP hoy",
        "tipo": "bueno",
        "efecto": {"vip_chance": 0.1},
        "probabilidad": 0.03
    },
    "combo_dia": {
        "nombre": "Combo del Dia",
        "desc": "Farmacos cuestan 50%",
        "tipo": "bueno",
        "efecto": {"descuento_dia": 50},
        "probabilidad": 0.01
    },
    
    # =========================================================================
    # EVENTOS MALOS (18 eventos)
    # =========================================================================
    "inspeccion": {
        "nombre": "Inspeccion",
        "desc": "Si >3 farmacos: -100E",
        "tipo": "malo",
        "efecto": {"multa_farmacos": 100, "limite": 3},
        "probabilidad": 0.05
    },
    "resaca": {
        "nombre": "Resaca",
        "desc": "-20% XP hoy",
        "tipo": "malo",
        "efecto": {"xp_mult": 0.8},
        "probabilidad": 0.05
    },
    "pacientes_dificiles": {
        "nombre": "Dia Dificil",
        "desc": "Pacientes +1 dificultad",
        "tipo": "malo",
        "efecto": {"dificultad_extra": 1},
        "probabilidad": 0.06
    },
    "escasez": {
        "nombre": "Escasez",
        "desc": "Tienda +50% precios",
        "tipo": "malo",
        "efecto": {"precio_extra": 50},
        "probabilidad": 0.04
    },
    "mala_prensa": {
        "nombre": "Mala Prensa",
        "desc": "-1 paciente hoy",
        "tipo": "malo",
        "efecto": {"pacientes_menos": 1},
        "probabilidad": 0.05
    },
    "impuestos": {
        "nombre": "Impuestos",
        "desc": "Hacienda cobra 10%",
        "tipo": "malo",
        "efecto": {"impuesto": 0.1},
        "probabilidad": 0.03
    },
    "robo": {
        "nombre": "Robo!",
        "desc": "Pierdes 1 item aleatorio",
        "tipo": "malo",
        "efecto": {"pierde_item": True},
        "probabilidad": 0.02
    },
    "queja_vecinos": {
        "nombre": "Queja Vecinos",
        "desc": "Pacientes -1 tolerancia",
        "tipo": "malo",
        "efecto": {"tolerancia_menos": 1},
        "probabilidad": 0.04
    },
    "lunes": {
        "nombre": "Maldito Lunes",
        "desc": "-10% a todo",
        "tipo": "malo",
        "efecto": {"penalizacion_global": 0.1},
        "probabilidad": 0.05
    },
    "gripe": {
        "nombre": "Gripe",
        "desc": "Solo 2 pacientes hoy",
        "tipo": "malo",
        "efecto": {"max_pacientes": 2},
        "probabilidad": 0.03
    },
    "denuncia": {
        "nombre": "Denuncia",
        "desc": "Multa de 150E",
        "tipo": "malo",
        "efecto": {"multa": 150},
        "probabilidad": 0.02
    },
    "competencia": {
        "nombre": "Competencia",
        "desc": "Pacientes pagan -20%",
        "tipo": "malo",
        "efecto": {"dinero_mult": 0.8},
        "probabilidad": 0.04
    },
    "averia": {
        "nombre": "Averia",
        "desc": "Reparacion: -80E",
        "tipo": "malo",
        "efecto": {"multa": 80},
        "probabilidad": 0.03
    },
    "caos": {
        "nombre": "Caos Total",
        "desc": "Todo aleatorio hoy",
        "tipo": "malo",
        "efecto": {"aleatorio": True},
        "probabilidad": 0.02
    },
    "morosos_dia": {
        "nombre": "Dia de Morosos",
        "desc": "50% pacientes no pagan",
        "tipo": "malo",
        "efecto": {"moroso_chance": 0.5},
        "probabilidad": 0.03
    },
    "confiscacion": {
        "nombre": "Confiscacion",
        "desc": "Pierdes todos los items",
        "tipo": "malo",
        "efecto": {"pierde_todo": True},
        "probabilidad": 0.01
    },
    "huelga": {
        "nombre": "Huelga",
        "desc": "Tienda cerrada hoy",
        "tipo": "malo",
        "efecto": {"tienda_cerrada": True},
        "probabilidad": 0.03
    },
    "fuga_gas": {
        "nombre": "Fuga de Gas",
        "desc": "Solo 1 paciente hoy",
        "tipo": "malo",
        "efecto": {"max_pacientes": 1},
        "probabilidad": 0.02
    },
    
    # =========================================================================
    # EVENTOS NEUTROS/ESPECIALES (14 eventos)
    # =========================================================================
    "dia_normal": {
        "nombre": "Dia Normal",
        "desc": "Nada especial",
        "tipo": "neutro",
        "efecto": {},
        "probabilidad": 0.12
    },
    "paciente_misterioso": {
        "nombre": "Misterioso",
        "desc": "Aparece paciente ???",
        "tipo": "especial",
        "efecto": {"fuerza_tipo": "misterioso"},
        "probabilidad": 0.01
    },
    "visita_camello": {
        "nombre": "Visita Camello",
        "desc": "Compra sin ir a tienda",
        "tipo": "especial",
        "efecto": {"tienda_portatil": True},
        "probabilidad": 0.02
    },
    "eclipse": {
        "nombre": "Eclipse",
        "desc": "Todo invertido hoy",
        "tipo": "especial",
        "efecto": {"invertido": True},
        "probabilidad": 0.01
    },
    "deja_vu": {
        "nombre": "Deja Vu",
        "desc": "Mismo evento que ayer",
        "tipo": "especial",
        "efecto": {"repite": True},
        "probabilidad": 0.02
    },
    "celebridad_viene": {
        "nombre": "Celebridad",
        "desc": "Viene una Celebridad!",
        "tipo": "especial",
        "efecto": {"fuerza_tipo": "celebridad"},
        "probabilidad": 0.005
    },
    "gemelos_vienen": {
        "nombre": "Gemelos!",
        "desc": "Vienen Gemelos",
        "tipo": "especial",
        "efecto": {"fuerza_tipo": "gemelos"},
        "probabilidad": 0.01
    },
    "guardia": {
        "nombre": "Guardia Nocturna",
        "desc": "Emergencias toda la noche",
        "tipo": "especial",
        "efecto": {"guardia_nocturna": True},
        "probabilidad": 0.02
    },
    "lluvia": {
        "nombre": "Dia Lluvioso",
        "desc": "Pacientes mas tristes",
        "tipo": "especial",
        "efecto": {"depresivos_extra": True},
        "probabilidad": 0.03
    },
    "viernes_13": {
        "nombre": "Viernes 13",
        "desc": "Mala suerte garantizada",
        "tipo": "especial",
        "efecto": {"mala_suerte": True},
        "probabilidad": 0.01
    },
    "black_friday": {
        "nombre": "Black Friday",
        "desc": "TODO -50% (tienda+mejoras)",
        "tipo": "especial",
        "efecto": {"descuento_total": 50},
        "probabilidad": 0.01
    },
    "auditoria": {
        "nombre": "Auditoria",
        "desc": "Bonus x2 si no usas drogas",
        "tipo": "especial",
        "efecto": {"auditoria": True},
        "probabilidad": 0.02
    },
    "retiro": {
        "nombre": "Retiro Espiritual",
        "desc": "XP x2, Dinero x0.5",
        "tipo": "especial",
        "efecto": {"xp_mult": 2.0, "dinero_mult": 0.5},
        "probabilidad": 0.02
    },
    "ruleta": {
        "nombre": "Ruleta Rusa",
        "desc": "50% muy bueno, 50% muy malo",
        "tipo": "especial",
        "efecto": {"ruleta": True},
        "probabilidad": 0.01
    },
}


# ============================================================================
# SISTEMA DE RACHAS
# ============================================================================

RACHAS = {
    # =========================================================================
    # RACHA DE ACIERTOS - Principal
    # =========================================================================
    "aciertos": {
        "nombre": "Racha Aciertos",
        "multiplicadores": {
            3: 1.1,    # x1.1 a los 3 aciertos
            5: 1.25,   # x1.25 a los 5
            7: 1.4,    # x1.4 a los 7
            10: 1.6,   # x1.6 a los 10
            15: 2.0,   # x2 a los 15
            20: 2.5,   # x2.5 a los 20
            30: 3.0,   # x3 a los 30
            50: 4.0,   # x4 a los 50
            100: 5.0,  # x5 a los 100!
        },
        "bonus_texto": [
            (3, "Buena racha!"),
            (5, "En forma!"),
            (7, "Caliente!"),
            (10, "EN LLAMAS!"),
            (15, "IMPARABLE!"),
            (20, "DIOS!"),
            (30, "LEYENDA!"),
            (50, "MITICO!"),
            (100, "INMORTAL!"),
        ],
        "bonus_dinero": {
            10: 50,
            20: 150,
            30: 300,
            50: 500,
            100: 1000,
        }
    },
    
    # =========================================================================
    # RACHA DE CURADOS - Sin huidas
    # =========================================================================
    "curados": {
        "nombre": "Racha Curados",
        "multiplicadores": {
            2: 1.1,
            3: 1.2,
            5: 1.4,
            7: 1.6,
            10: 2.0,
            15: 2.5,
            20: 3.0,
        },
        "bonus_texto": [
            (2, "2 seguidos!"),
            (3, "Trio!"),
            (5, "Quintuple!"),
            (7, "Racha Epica!"),
            (10, "HEROICO!"),
            (15, "LEGENDARIO!"),
            (20, "DIVINO!"),
        ],
        "bonus_dinero": {
            5: 100,
            10: 300,
            15: 600,
            20: 1000,
        }
    },
    
    # =========================================================================
    # RACHA DE FALLOS - "Logros" negativos
    # =========================================================================
    "fallos": {
        "nombre": "Mala Racha",
        "multiplicadores": {
            3: 0.9,    # Penalización
            5: 0.8,
            7: 0.7,
            10: 0.5,
        },
        "bonus_texto": [
            (3, "Mala racha..."),
            (5, "Desastroso..."),
            (7, "CATASTROFE"),
            (10, "APOCALIPSIS"),
        ],
        "efecto_especial": {
            5: "cafe_gratis",      # Te dan un café para animarte
            10: "paciente_facil",  # Siguiente paciente más fácil
        }
    },
    
    # =========================================================================
    # RACHA DE PERFECTOS - Pacientes sin fallar
    # =========================================================================
    "perfectos": {
        "nombre": "Curas Perfectas",
        "multiplicadores": {
            2: 1.2,
            3: 1.5,
            5: 2.0,
            7: 2.5,
            10: 3.0,
        },
        "bonus_texto": [
            (2, "Doble perfecto!"),
            (3, "Triple perfecto!"),
            (5, "CIRUJANO!"),
            (7, "MAESTRO!"),
            (10, "PERFECCION!"),
        ],
        "bonus_dinero": {
            3: 100,
            5: 250,
            7: 500,
            10: 1000,
        }
    },
    
    # =========================================================================
    # RACHA DIARIA - Días consecutivos jugando
    # =========================================================================
    "dias": {
        "nombre": "Dias Seguidos",
        "multiplicadores": {
            3: 1.05,
            7: 1.1,
            14: 1.2,
            30: 1.3,
            60: 1.5,
            100: 2.0,
        },
        "bonus_texto": [
            (3, "3 dias!"),
            (7, "1 semana!"),
            (14, "2 semanas!"),
            (30, "1 MES!"),
            (60, "2 MESES!"),
            (100, "100 DIAS!"),
        ],
        "bonus_dinero": {
            7: 100,
            14: 200,
            30: 500,
            60: 1000,
            100: 2000,
        }
    },
    
    # =========================================================================
    # RACHA VIP - Pacientes VIP consecutivos
    # =========================================================================
    "vip": {
        "nombre": "Racha VIP",
        "multiplicadores": {
            2: 1.3,
            3: 1.5,
            5: 2.0,
        },
        "bonus_texto": [
            (2, "VIP x2!"),
            (3, "VIP x3!"),
            (5, "REY DE VIPS!"),
        ],
        "bonus_dinero": {
            2: 100,
            3: 300,
            5: 700,
        }
    },
}


# ============================================================================
# FUNCIONES DE LOGROS
# ============================================================================

def get_logros_desbloqueados(data):
    """Obtiene lista de logros desbloqueados"""
    if "logros" not in data:
        data["logros"] = {"desbloqueados": [], "notificados": []}
    return data["logros"]["desbloqueados"]


def check_logros(data):
    """
    Comprueba y desbloquea logros pendientes.
    Returns lista de logros recién desbloqueados.
    """
    if "logros" not in data:
        data["logros"] = {"desbloqueados": [], "notificados": []}
    
    desbloqueados = data["logros"]["desbloqueados"]
    nuevos = []
    
    # Stats para comprobar
    stats = data["jugador"]["stats"]
    economia = data.get("economia", {})
    
    valores = {
        "pacientes_curados": stats.get("pacientes_curados", 0),
        "pacientes_abandonados": stats.get("pacientes_abandonados", 0),
        "sesiones_correctas": stats.get("sesiones_correctas", 0),
        "sesiones_incorrectas": stats.get("sesiones_incorrectas", 0),
        "total_ganado": economia.get("total_ganado", 0),
        "total_gastado": economia.get("total_gastado", 0),
        "dinero_max": stats.get("dinero_max", 0),
        "nivel": data["jugador"].get("nivel", 1),
        "racha_aciertos_max": stats.get("racha_aciertos_max", 0),
        "racha_curados": stats.get("racha_curados", 0),
        "farmacos_usados": stats.get("farmacos_usados", 0),
        "suero_usado": stats.get("suero_usado", 0),
        "camisa_usada": stats.get("camisa_usada", 0),
        "tipos_farmacos": len(stats.get("tipos_farmacos_usados", [])),
        "curas_perfectas": stats.get("curas_perfectas", 0),
        "curas_rapidas": stats.get("curas_rapidas", 0),
        "pacientes_dificiles": stats.get("pacientes_dificiles", 0),
    }
    
    for logro_id, logro in LOGROS.items():
        if logro_id in desbloqueados:
            continue
        
        campo, operador, valor = logro["condicion"]
        actual = valores.get(campo, 0)
        
        cumple = False
        if operador == ">=":
            cumple = actual >= valor
        elif operador == "==":
            cumple = actual == valor
        elif operador == ">":
            cumple = actual > valor
        
        if cumple:
            desbloqueados.append(logro_id)
            nuevos.append(logro_id)
    
    return nuevos


def aplicar_recompensa_logro(data, logro_id):
    """Aplica la recompensa de un logro"""
    from career_data import add_dinero, add_item
    
    logro = LOGROS.get(logro_id)
    if not logro:
        return None
    
    recompensa = logro.get("recompensa", {})
    resultado = {"logro": logro["nombre"], "items": []}
    
    if "dinero" in recompensa:
        add_dinero(data, recompensa["dinero"])
        resultado["items"].append(f"+{recompensa['dinero']}E")
    
    if "item" in recompensa:
        add_item(data, recompensa["item"])
        resultado["items"].append(f"+1 farmaco")
    
    if "titulo" in recompensa:
        if "titulos_disponibles" not in data["jugador"]:
            data["jugador"]["titulos_disponibles"] = []
        data["jugador"]["titulos_disponibles"].append(recompensa["titulo"])
        resultado["items"].append(f"Titulo: {recompensa['titulo']}")
    
    if "descuento" in recompensa:
        if "descuento_logros" not in data:
            data["descuento_logros"] = 0
        data["descuento_logros"] += recompensa["descuento"]
        resultado["items"].append(f"-{recompensa['descuento']}% tienda")
    
    return resultado


# ============================================================================
# FUNCIONES DE RACHAS
# ============================================================================

def get_racha_actual(data):
    """Obtiene racha actual de aciertos"""
    return data["jugador"]["stats"].get("racha_actual", 0)


def incrementar_racha(data, tipo="aciertos"):
    """Incrementa racha y devuelve multiplicador si hay bonus"""
    stats = data["jugador"]["stats"]
    
    racha_key = f"racha_{tipo}_actual"
    max_key = f"racha_{tipo}_max"
    
    stats[racha_key] = stats.get(racha_key, 0) + 1
    racha = stats[racha_key]
    
    # Actualizar máximo
    if racha > stats.get(max_key, 0):
        stats[max_key] = racha
    
    # Calcular multiplicador
    config = RACHAS.get(tipo, {})
    mults = config.get("multiplicadores", {})
    
    mult = 1.0
    texto = None
    
    for umbral in sorted(mults.keys(), reverse=True):
        if racha >= umbral:
            mult = mults[umbral]
            break
    
    for umbral, msg in config.get("bonus_texto", []):
        if racha == umbral:
            texto = msg
            break
    
    return {"multiplicador": mult, "racha": racha, "texto": texto}


def romper_racha(data, tipo="aciertos"):
    """Rompe la racha actual"""
    racha_key = f"racha_{tipo}_actual"
    data["jugador"]["stats"][racha_key] = 0


# ============================================================================
# FUNCIONES DE MEJORAS
# ============================================================================

def get_mejoras_compradas(data):
    """Obtiene lista de mejoras compradas"""
    if "mejoras" not in data:
        data["mejoras"] = []
    return data["mejoras"]


def tiene_mejora(data, mejora_id):
    """Comprueba si tiene una mejora"""
    return mejora_id in get_mejoras_compradas(data)


def puede_comprar_mejora(data, mejora_id):
    """Comprueba si puede comprar una mejora"""
    from career_data import get_dinero
    
    if mejora_id in get_mejoras_compradas(data):
        return False, "Ya comprada"
    
    mejora = MEJORAS.get(mejora_id)
    if not mejora:
        return False, "No existe"
    
    # Comprobar requisito
    req = mejora.get("requisito")
    if req and req not in get_mejoras_compradas(data):
        return False, f"Necesitas: {MEJORAS[req]['nombre']}"
    
    # Comprobar dinero
    dinero = get_dinero(data)
    precio = mejora["precio"]
    
    # Aplicar descuentos
    descuento = data.get("descuento_logros", 0)
    precio = int(precio * (100 - descuento) / 100)
    
    if dinero < precio:
        return False, "Sin pasta"
    
    return True, precio


def comprar_mejora(data, mejora_id):
    """Compra una mejora. Returns (exito, mensaje)"""
    from career_data import add_dinero
    
    puede, resultado = puede_comprar_mejora(data, mejora_id)
    if not puede:
        return False, resultado
    
    precio = resultado
    add_dinero(data, -precio)
    get_mejoras_compradas(data).append(mejora_id)
    
    return True, MEJORAS[mejora_id]["nombre"]


def get_efecto_mejoras(data, efecto_key):
    """Obtiene el valor de un efecto de las mejoras compradas"""
    valor = 0
    for mejora_id in get_mejoras_compradas(data):
        mejora = MEJORAS.get(mejora_id, {})
        efectos = mejora.get("efecto", {})
        if efecto_key in efectos:
            val = efectos[efecto_key]
            if isinstance(val, bool):
                return val
            elif isinstance(val, (int, float)):
                valor += val
    return valor


# ============================================================================
# FUNCIONES DE EVENTOS
# ============================================================================

def generar_evento_diario(data):
    """Genera el evento del día"""
    # Comprobar si ya hay evento hoy
    evento_actual = data.get("evento_hoy", {})
    fecha_evento = evento_actual.get("fecha", "")
    
    from career_data import get_ultimo_dia_jugado
    hoy = get_ultimo_dia_jugado(data)
    
    if fecha_evento == hoy:
        return evento_actual
    
    # Generar nuevo evento
    # Comprobar deja vu
    if evento_actual.get("id") and random.random() < 0.03:
        # Repetir evento anterior
        evento_actual["fecha"] = hoy
        data["evento_hoy"] = evento_actual
        return evento_actual
    
    # Seleccionar evento por probabilidad
    r = random.random()
    acumulado = 0
    evento_seleccionado = "dia_normal"
    
    for evento_id, evento in EVENTOS.items():
        acumulado += evento["probabilidad"]
        if r <= acumulado:
            evento_seleccionado = evento_id
            break
    
    evento = EVENTOS[evento_seleccionado].copy()
    evento["id"] = evento_seleccionado
    evento["fecha"] = hoy
    
    data["evento_hoy"] = evento
    return evento


def get_evento_hoy(data):
    """Obtiene el evento del día actual"""
    return data.get("evento_hoy", {"nombre": "Normal", "efecto": {}})


def aplicar_efecto_evento(data, efecto_key, valor_base):
    """Aplica modificador de evento a un valor"""
    evento = get_evento_hoy(data)
    efectos = evento.get("efecto", {})
    
    if efecto_key in efectos:
        mod = efectos[efecto_key]
        if isinstance(mod, bool):
            return mod
        elif isinstance(mod, float) and mod != 1.0:
            return int(valor_base * mod)
        elif isinstance(mod, int):
            return valor_base + mod
    
    return valor_base


# ============================================================================
# FUNCIONES DE PACIENTES ESPECIALES
# ============================================================================

def seleccionar_tipo_paciente(data):
    """Selecciona tipo de paciente aleatorio"""
    evento = get_evento_hoy(data)
    
    # Comprobar si evento fuerza un tipo
    if "fuerza_tipo" in evento.get("efecto", {}):
        return evento["efecto"]["fuerza_tipo"]
    
    # Selección normal por probabilidad
    r = random.random()
    acumulado = 0
    
    for tipo_id, tipo in TIPOS_PACIENTE.items():
        acumulado += tipo["probabilidad"]
        if r <= acumulado:
            return tipo_id
    
    return "normal"


def get_modificadores_paciente(tipo_id):
    """Obtiene modificadores de un tipo de paciente"""
    tipo = TIPOS_PACIENTE.get(tipo_id, TIPOS_PACIENTE["normal"])
    return tipo.get("modificadores", {})


def aplicar_modificadores_paciente(paciente, tipo_id, data):
    """Aplica modificadores de tipo especial al paciente"""
    mods = get_modificadores_paciente(tipo_id)
    mejoras = get_mejoras_compradas(data)
    
    # Guardar tipo en paciente
    paciente["tipo"] = tipo_id
    paciente["tipo_nombre"] = TIPOS_PACIENTE[tipo_id]["nombre"]
    
    # Sesiones
    if "sesiones_mult" in mods:
        paciente["sesiones_totales"] = max(3, int(
            paciente["sesiones_totales"] * mods["sesiones_mult"]
        ))
    
    # Modificador de mejora: reduce sesiones
    if "divan_premium" in mejoras:
        paciente["sesiones_totales"] = max(3, 
            paciente["sesiones_totales"] - 1)
    
    # Tolerancia (progreso mínimo antes de huir)
    tolerancia_base = -3
    if "tolerancia" in mods:
        tolerancia_base += mods["tolerancia"]
    if "planta_bonita" in mejoras:
        tolerancia_base -= 1  # Aguanta más
    paciente["tolerancia"] = tolerancia_base
    
    # Guardar multiplicadores de dinero/xp
    paciente["dinero_mult"] = mods.get("dinero_mult", 1.0)
    paciente["xp_mult"] = mods.get("xp_mult", 1.0)
    
    # Flags especiales
    if mods.get("trae_pacientes"):
        paciente["trae_pacientes"] = mods["trae_pacientes"]
    if mods.get("vuelve"):
        paciente["vuelve"] = True
    if mods.get("tiempo_limite"):
        paciente["tiempo_limite"] = True
    if mods.get("sin_info"):
        paciente["sin_info"] = True
        paciente["nombre"] = "???"
        paciente["edad"] = "???"
        paciente["sexo"] = "???"
        paciente["ocupacion"] = "???"
    
    return paciente


# ============================================================================
# FUNCION AUXILIAR: Actualizar stats para logros
# ============================================================================

def registrar_stat_logro(data, stat_key, valor=1, modo="incrementar"):
    """Registra un stat para logros"""
    stats = data["jugador"]["stats"]
    
    if modo == "incrementar":
        stats[stat_key] = stats.get(stat_key, 0) + valor
    elif modo == "establecer":
        stats[stat_key] = valor
    elif modo == "maximo":
        stats[stat_key] = max(stats.get(stat_key, 0), valor)
    elif modo == "lista_agregar":
        if stat_key not in stats:
            stats[stat_key] = []
        if valor not in stats[stat_key]:
            stats[stat_key].append(valor)
    
    # Actualizar dinero máximo
    from career_data import get_dinero
    dinero = get_dinero(data)
    stats["dinero_max"] = max(stats.get("dinero_max", 0), dinero)


# ============================================================================
# MISIONES DIARIAS Y SEMANALES
# ============================================================================

MISIONES_DIARIAS = {
    "madrugador": {
        "nombre": "Madrugador",
        "desc": "Responde antes 10:00",
        "tipo": "hora",
        "condicion": {"antes_hora": 10},
        "recompensa": {"dinero": 50}
    },
    "sin_drogas": {
        "nombre": "Sin Drogas",
        "desc": "Cura 1 sin farmacos",
        "tipo": "curar_limpio",
        "condicion": {"curar_sin_farmacos": 1},
        "recompensa": {"dinero": 100}
    },
    "racha_mini": {
        "nombre": "Racha Mini",
        "desc": "Racha de 5 aciertos",
        "tipo": "racha",
        "condicion": {"racha_min": 5},
        "recompensa": {"dinero": 75}
    },
    "buen_doctor": {
        "nombre": "El Buen Doctor",
        "desc": "3 aciertos seguidos",
        "tipo": "racha",
        "condicion": {"racha_min": 3},
        "recompensa": {"dinero": 50}
    },
    "farmaceutico": {
        "nombre": "Farmaceutico",
        "desc": "Usa 2 farmacos hoy",
        "tipo": "farmacos",
        "condicion": {"farmacos_usados": 2},
        "recompensa": {"dinero": 60}
    },
    "trabajador": {
        "nombre": "Trabajador",
        "desc": "Completa 5 sesiones",
        "tipo": "sesiones",
        "condicion": {"sesiones": 5},
        "recompensa": {"dinero": 80}
    },
    "perfeccionista_dia": {
        "nombre": "Perfecto Dia",
        "desc": "100% aciertos hoy (min 3)",
        "tipo": "precision",
        "condicion": {"precision": 100, "min_sesiones": 3},
        "recompensa": {"dinero": 120}
    },
    "nocturno": {
        "nombre": "Nocturno",
        "desc": "Responde despues 22:00",
        "tipo": "hora",
        "condicion": {"despues_hora": 22},
        "recompensa": {"dinero": 50}
    },
    "economico": {
        "nombre": "Economico",
        "desc": "Gana 200E hoy",
        "tipo": "dinero",
        "condicion": {"dinero_ganado": 200},
        "recompensa": {"dinero": 50}
    },
    "vip_hunter": {
        "nombre": "Caza VIPs",
        "desc": "Atiende 1 VIP",
        "tipo": "paciente_tipo",
        "condicion": {"tipo": "vip", "cantidad": 1},
        "recompensa": {"dinero": 100}
    }
}

MISIONES_SEMANALES = {
    "curandero_sem": {
        "nombre": "Curandero",
        "desc": "Cura 5 pacientes",
        "tipo": "curar",
        "condicion": {"curar": 5},
        "recompensa": {"dinero": 300, "item": "ansio"}
    },
    "intocable": {
        "nombre": "Intocable",
        "desc": "20 aciertos sin fallo",
        "tipo": "racha_max",
        "condicion": {"racha_max": 20},
        "recompensa": {"dinero": 500}
    },
    "magnate_sem": {
        "nombre": "El Magnate",
        "desc": "Gana 1000E",
        "tipo": "dinero",
        "condicion": {"dinero_ganado": 1000},
        "recompensa": {"dinero": 200}
    },
    "coleccionista_sem": {
        "nombre": "Coleccionista",
        "desc": "Usa 5 farmacos dif.",
        "tipo": "farmacos_tipos",
        "condicion": {"tipos_farmacos": 5},
        "recompensa": {"item": "suero"}
    },
    "sin_bajas_sem": {
        "nombre": "Sin Bajas",
        "desc": "0 huidos esta semana",
        "tipo": "sin_huidos",
        "condicion": {"huidos_max": 0},
        "recompensa": {"dinero": 400}
    },
    "veterano": {
        "nombre": "Veterano",
        "desc": "30 sesiones completadas",
        "tipo": "sesiones",
        "condicion": {"sesiones": 30},
        "recompensa": {"dinero": 350}
    },
    "multitarea": {
        "nombre": "Multitarea",
        "desc": "Cura 3 tipos diferentes",
        "tipo": "tipos_curados",
        "condicion": {"tipos": 3},
        "recompensa": {"dinero": 250, "item": "cafe"}
    }
}


def generar_misiones_diarias(data, cantidad=3):
    """Genera misiones diarias aleatorias"""
    disponibles = list(MISIONES_DIARIAS.keys())
    random.shuffle(disponibles)
    
    misiones = []
    for i in range(min(cantidad, len(disponibles))):
        mid = disponibles[i]
        mision = MISIONES_DIARIAS[mid].copy()
        mision["id"] = mid
        mision["progreso"] = 0
        mision["completada"] = False
        mision["reclamada"] = False
        misiones.append(mision)
    
    data["misiones"]["diarias"] = misiones
    data["misiones"]["dia_generadas"] = data["config"].get("ultimo_dia_jugado", "")
    return misiones


def generar_misiones_semanales(data, cantidad=3):
    """Genera misiones semanales"""
    disponibles = list(MISIONES_SEMANALES.keys())
    random.shuffle(disponibles)
    
    misiones = []
    for i in range(min(cantidad, len(disponibles))):
        mid = disponibles[i]
        mision = MISIONES_SEMANALES[mid].copy()
        mision["id"] = mid
        mision["progreso"] = 0
        mision["completada"] = False
        mision["reclamada"] = False
        misiones.append(mision)
    
    data["misiones"]["semanales"] = misiones
    return misiones


def actualizar_progreso_mision(data, tipo_evento, valor=1, extra=None):
    """Actualiza progreso de misiones según evento"""
    for mision in data.get("misiones", {}).get("diarias", []):
        if mision["completada"]:
            continue
        _check_mision_progreso(mision, tipo_evento, valor, extra)
    
    for mision in data.get("misiones", {}).get("semanales", []):
        if mision["completada"]:
            continue
        _check_mision_progreso(mision, tipo_evento, valor, extra)


def _check_mision_progreso(mision, tipo_evento, valor, extra):
    """Comprueba y actualiza progreso de una misión"""
    if mision["tipo"] == "racha" and tipo_evento == "racha":
        if valor >= mision["condicion"].get("racha_min", 0):
            mision["completada"] = True
    elif mision["tipo"] == "sesiones" and tipo_evento == "sesion":
        mision["progreso"] += 1
        if mision["progreso"] >= mision["condicion"].get("sesiones", 1):
            mision["completada"] = True
    elif mision["tipo"] == "curar" and tipo_evento == "curar":
        mision["progreso"] += 1
        if mision["progreso"] >= mision["condicion"].get("curar", 1):
            mision["completada"] = True
    elif mision["tipo"] == "farmacos" and tipo_evento == "farmaco":
        mision["progreso"] += 1
        if mision["progreso"] >= mision["condicion"].get("farmacos_usados", 1):
            mision["completada"] = True
    elif mision["tipo"] == "dinero" and tipo_evento == "dinero":
        mision["progreso"] += valor
        if mision["progreso"] >= mision["condicion"].get("dinero_ganado", 100):
            mision["completada"] = True
    elif mision["tipo"] == "hora" and tipo_evento == "hora":
        antes = mision["condicion"].get("antes_hora")
        despues = mision["condicion"].get("despues_hora")
        if antes and valor < antes:
            mision["completada"] = True
        if despues and valor >= despues:
            mision["completada"] = True
    elif mision["tipo"] == "curar_limpio" and tipo_evento == "curar_limpio":
        mision["progreso"] += 1
        if mision["progreso"] >= mision["condicion"].get("curar_sin_farmacos", 1):
            mision["completada"] = True
    elif mision["tipo"] == "paciente_tipo" and tipo_evento == "paciente_tipo":
        if extra == mision["condicion"].get("tipo"):
            mision["progreso"] += 1
            if mision["progreso"] >= mision["condicion"].get("cantidad", 1):
                mision["completada"] = True


def reclamar_mision(data, mision_id, es_diaria=True):
    """Reclama recompensa de misión completada"""
    lista = "diarias" if es_diaria else "semanales"
    for mision in data.get("misiones", {}).get(lista, []):
        if mision["id"] == mision_id and mision["completada"] and not mision["reclamada"]:
            mision["reclamada"] = True
            return mision["recompensa"]
    return None


def get_misiones_activas(data):
    """Obtiene misiones activas (no reclamadas)"""
    resultado = {
        "diarias": [],
        "semanales": []
    }
    for m in data.get("misiones", {}).get("diarias", []):
        if not m.get("reclamada"):
            resultado["diarias"].append(m)
    for m in data.get("misiones", {}).get("semanales", []):
        if not m.get("reclamada"):
            resultado["semanales"].append(m)
    return resultado


# ============================================================================
# SISTEMA DE REPUTACIÓN
# ============================================================================

RANGOS_REPUTACION = {
    "carnicero": {"min": -100, "max": -50, "nombre": "Carnicero", "efecto": {"dinero_mult": 0.8, "solo_pobres": True}},
    "chapucero": {"min": -50, "max": -20, "nombre": "Chapucero", "efecto": {"dinero_mult": 0.9}},
    "novato": {"min": -20, "max": 20, "nombre": "Novato", "efecto": {}},
    "respetable": {"min": 20, "max": 50, "nombre": "Respetable", "efecto": {"vip_bonus": 0.1}},
    "eminencia": {"min": 50, "max": 80, "nombre": "Eminencia", "efecto": {"dinero_mult": 1.2, "vip_bonus": 0.2}},
    "leyenda": {"min": 80, "max": 100, "nombre": "Leyenda", "efecto": {"dinero_mult": 2.0, "vip_bonus": 0.3, "misterioso_bonus": 0.05}}
}

CAMBIOS_REPUTACION = {
    "curar_normal": 3,
    "curar_dificil": 7,
    "curar_vip": 15,
    "curar_misterioso": 20,
    "huye_normal": -5,
    "huye_vip": -25,
    "usar_camisa": -5,
    "perfecto": 5,  # Sin fallos
    "racha_10": 3,
    "racha_20": 5
}


def get_reputacion(data):
    """Obtiene reputación actual"""
    return data.get("reputacion", {}).get("valor", 0)


def get_rango_reputacion(data):
    """Obtiene rango de reputación actual"""
    rep = get_reputacion(data)
    for rango_id, rango in RANGOS_REPUTACION.items():
        if rango["min"] <= rep <= rango["max"]:
            return rango_id, rango
    return "novato", RANGOS_REPUTACION["novato"]


def modificar_reputacion(data, cantidad, razon=""):
    """Modifica la reputación"""
    if "reputacion" not in data:
        data["reputacion"] = {"valor": 0, "historial": []}
    
    viejo = data["reputacion"]["valor"]
    nuevo = max(-100, min(100, viejo + cantidad))
    data["reputacion"]["valor"] = nuevo
    
    # Registrar cambio
    data["reputacion"]["historial"].append({
        "cambio": cantidad,
        "razon": razon,
        "nuevo": nuevo
    })
    # Mantener solo últimos 20
    data["reputacion"]["historial"] = data["reputacion"]["historial"][-20:]
    
    # Comprobar cambio de rango
    viejo_rango, _ = _get_rango_por_valor(viejo)
    nuevo_rango, _ = _get_rango_por_valor(nuevo)
    
    return {
        "viejo": viejo,
        "nuevo": nuevo,
        "cambio_rango": viejo_rango != nuevo_rango,
        "rango": nuevo_rango
    }


def _get_rango_por_valor(valor):
    """Obtiene rango por valor de reputación"""
    for rango_id, rango in RANGOS_REPUTACION.items():
        if rango["min"] <= valor <= rango["max"]:
            return rango_id, rango
    return "novato", RANGOS_REPUTACION["novato"]


def get_efectos_reputacion(data):
    """Obtiene efectos del rango actual"""
    _, rango = get_rango_reputacion(data)
    return rango.get("efecto", {})


# ============================================================================
# SISTEMA DE CRAFTING
# ============================================================================

RECETAS = {
    "placebo_dorado": {
        "nombre": "Placebo Dorado",
        "desc": "75% de funcionar",
        "ingredientes": [("placebo", 2)],
        "resultado": {
            "id": "placebo_dorado",
            "nombre": "Placebo Dorado",
            "precio": 200,
            "desc": "75% de funcionar",
            "efecto": "placebo_75",
            "raro": False
        }
    },
    "speed": {
        "nombre": "Speed",
        "desc": "x3 XP una sesion",
        "ingredientes": [("cafe", 1), ("vitaminas", 1)],
        "resultado": {
            "id": "speed",
            "nombre": "Speed",
            "precio": 250,
            "desc": "x3 XP una sesion",
            "efecto": "triple_xp",
            "raro": False
        }
    },
    "coma_inducido": {
        "nombre": "Coma Inducido",
        "desc": "-3 sesiones",
        "ingredientes": [("ansio", 1), ("sedante", 1)],
        "resultado": {
            "id": "coma",
            "nombre": "Coma Inducido",
            "precio": 600,
            "desc": "-3 sesiones",
            "efecto": "reduce_sesion_3",
            "raro": False
        }
    },
    "mindcontrol": {
        "nombre": "Mindcontrol",
        "desc": "Elimina 2 opciones",
        "ingredientes": [("electro", 1), ("suero", 1)],
        "resultado": {
            "id": "mindcontrol",
            "nombre": "Mindcontrol",
            "precio": 1500,
            "desc": "Elimina 2 opciones",
            "efecto": "elimina_2_opciones",
            "raro": True
        }
    },
    "viaje_astral": {
        "nombre": "Viaje Astral",
        "desc": "Revela + protege",
        "ingredientes": [("hipno", 1), ("lsd", 1)],
        "resultado": {
            "id": "viaje",
            "nombre": "Viaje Astral",
            "precio": 2000,
            "desc": "Revela todo + protege",
            "efecto": "revela_protege",
            "raro": True
        }
    },
    "super_placebo": {
        "nombre": "Super Placebo",
        "desc": "100% funciona",
        "ingredientes": [("placebo_dorado", 2)],
        "resultado": {
            "id": "super_placebo",
            "nombre": "Super Placebo",
            "precio": 500,
            "desc": "100% funciona",
            "efecto": "placebo_100",
            "raro": False
        }
    },
    "coctel_letal": {
        "nombre": "Coctel Letal",
        "desc": "Cura o mata (50/50)",
        "ingredientes": [("experimental", 1), ("adrenalina", 1)],
        "resultado": {
            "id": "coctel",
            "nombre": "Coctel Letal",
            "precio": 3500,
            "desc": "Cura o huye 50/50",
            "efecto": "ruleta_rusa",
            "raro": True
        }
    },
    "zombificador": {
        "nombre": "Zombificador",
        "desc": "Paciente es zombie",
        "ingredientes": [("zombi", 1), ("lobo", 1)],
        "resultado": {
            "id": "zombificador",
            "nombre": "Zombificador",
            "precio": 4000,
            "desc": "No huye + no pierde prog",
            "efecto": "zombie_total",
            "raro": True
        }
    }
}


def puede_craftear(data, receta_id):
    """Comprueba si puede craftear una receta"""
    if receta_id not in RECETAS:
        return False, "Receta desconocida"
    
    # Comprobar si tiene mesa de crafting
    if not tiene_mejora(data, "mesa_crafting"):
        return False, "Necesitas Mesa Crafting"
    
    receta = RECETAS[receta_id]
    inventario = data.get("inventario", [])
    
    for item_id, cantidad in receta["ingredientes"]:
        tiene = sum(1 for i in inventario if i.get("id") == item_id)
        if tiene < cantidad:
            return False, f"Falta {item_id}"
    
    return True, "OK"


def craftear(data, receta_id):
    """Realiza el crafteo de una receta"""
    puede, msg = puede_craftear(data, receta_id)
    if not puede:
        return False, msg
    
    receta = RECETAS[receta_id]
    
    # Quitar ingredientes
    for item_id, cantidad in receta["ingredientes"]:
        for _ in range(cantidad):
            for i, item in enumerate(data["inventario"]):
                if item.get("id") == item_id:
                    data["inventario"].pop(i)
                    break
    
    # Añadir resultado
    data["inventario"].append(receta["resultado"].copy())
    
    # Registrar para logros
    registrar_stat_logro(data, "items_crafteados")
    
    return True, receta["resultado"]["nombre"]


def get_recetas_disponibles(data):
    """Lista recetas que puede craftear"""
    disponibles = []
    for rid, receta in RECETAS.items():
        puede, _ = puede_craftear(data, rid)
        disponibles.append({
            "id": rid,
            "receta": receta,
            "puede": puede
        })
    return disponibles


# ============================================================================
# CASOS FAMILIARES (Arcos Narrativos)
# ============================================================================

CASOS_FAMILIARES = {
    "familia_disfuncional": {
        "nombre": "Familia Disfuncional",
        "desc": "Una familia con problemas",
        "miembros": [
            {"rol": "Padre", "problema": "Adicto al trabajo", "personalidad": "Estresado"},
            {"rol": "Madre", "problema": "Compras compulsivas", "personalidad": "Ansiosa"},
            {"rol": "Hijo", "problema": "Adicto a videojuegos", "personalidad": "Apatico"},
            {"rol": "Abuela", "problema": "Cleptomana", "personalidad": "Senil graciosa"}
        ],
        "recompensa": {"dinero": 1000, "logro": "terapeuta_familiar"}
    },
    "los_ex": {
        "nombre": "Los Ex",
        "desc": "Problemas de pareja",
        "miembros": [
            {"rol": "El Ex", "problema": "No supera la ruptura", "personalidad": "Deprimido"},
            {"rol": "La Ex", "problema": "Tampoco la supera", "personalidad": "Vengativa"},
            {"rol": "El Nuevo", "problema": "Celos del ex", "personalidad": "Inseguro"},
            {"rol": "La Amante", "problema": "Culpabilidad", "personalidad": "Dramatica"}
        ],
        "recompensa": {"dinero": 800, "logro": "consejero_amoroso"}
    },
    "oficina_toxica": {
        "nombre": "La Oficina Toxica",
        "desc": "Companeros de trabajo",
        "miembros": [
            {"rol": "El Jefe", "problema": "Megalomania", "personalidad": "Narcisista"},
            {"rol": "El Pelota", "problema": "Baja autoestima", "personalidad": "Servil"},
            {"rol": "La Quemada", "problema": "Burnout severo", "personalidad": "Exhausta"},
            {"rol": "El Becario", "problema": "Sindrome impostor", "personalidad": "Nervioso"}
        ],
        "recompensa": {"dinero": 900, "logro": "coach_empresarial"}
    },
    "vecinos_infernales": {
        "nombre": "Vecinos Infernales",
        "desc": "Comunidad de vecinos",
        "miembros": [
            {"rol": "El Ruidoso", "problema": "No duerme de noche", "personalidad": "Fiestero"},
            {"rol": "La Cotilla", "problema": "Obsesion por espiar", "personalidad": "Entrometida"},
            {"rol": "El Presidente", "problema": "Delirios de poder", "personalidad": "Tirano"},
            {"rol": "El Moroso", "problema": "Fobia a pagar", "personalidad": "Escurridizo"}
        ],
        "recompensa": {"dinero": 750, "logro": "mediador_vecinal"}
    },
    "influencers": {
        "nombre": "Los Influencers",
        "desc": "Estrellas de internet",
        "miembros": [
            {"rol": "El Fitness", "problema": "Dismorfia corporal", "personalidad": "Obsesivo"},
            {"rol": "La Lifestyle", "problema": "Vida falsa", "personalidad": "Deprimida"},
            {"rol": "El Gamer", "problema": "Aislamiento social", "personalidad": "Antisocial"},
            {"rol": "La Coach", "problema": "Sindrome impostor", "personalidad": "Insegura"}
        ],
        "recompensa": {"dinero": 1200, "logro": "psicologo_tiktoker"}
    }
}


def iniciar_caso_familiar(data, caso_id):
    """Inicia un arco narrativo familiar"""
    if caso_id not in CASOS_FAMILIARES:
        return False
    
    caso = CASOS_FAMILIARES[caso_id]
    data["caso_activo"] = {
        "id": caso_id,
        "nombre": caso["nombre"],
        "miembros_total": len(caso["miembros"]),
        "miembros_curados": 0,
        "miembros_huidos": 0,
        "siguiente_idx": 0
    }
    return True


def get_siguiente_familiar(data):
    """Obtiene datos del siguiente miembro familiar"""
    caso = data.get("caso_activo")
    if not caso:
        return None
    
    caso_def = CASOS_FAMILIARES.get(caso["id"])
    if not caso_def:
        return None
    
    idx = caso["siguiente_idx"]
    if idx >= len(caso_def["miembros"]):
        return None
    
    return caso_def["miembros"][idx]


def completar_miembro_familiar(data, curado=True):
    """Marca un miembro como completado"""
    caso = data.get("caso_activo")
    if not caso:
        return None
    
    if curado:
        caso["miembros_curados"] += 1
    else:
        caso["miembros_huidos"] += 1
    
    caso["siguiente_idx"] += 1
    
    # Comprobar si completó el caso
    caso_def = CASOS_FAMILIARES.get(caso["id"])
    if caso["siguiente_idx"] >= caso_def["miembros_total"]:
        return finalizar_caso_familiar(data)
    
    return {"estado": "continua", "siguiente": get_siguiente_familiar(data)}


def finalizar_caso_familiar(data):
    """Finaliza un caso familiar y da recompensas"""
    caso = data.get("caso_activo")
    if not caso:
        return None
    
    caso_def = CASOS_FAMILIARES.get(caso["id"])
    resultado = {
        "completado": caso["miembros_curados"] == caso["miembros_total"],
        "curados": caso["miembros_curados"],
        "huidos": caso["miembros_huidos"],
        "total": caso["miembros_total"]
    }
    
    if resultado["completado"]:
        resultado["recompensa"] = caso_def["recompensa"]
    else:
        # Recompensa parcial
        resultado["recompensa"] = {
            "dinero": int(caso_def["recompensa"]["dinero"] * 
                        (caso["miembros_curados"] / caso["miembros_total"]))
        }
    
    data["caso_activo"] = None
    return resultado


def get_caso_activo(data):
    """Obtiene caso familiar activo"""
    return data.get("caso_activo")


# ============================================================================
# TORNEOS SEMANALES
# ============================================================================

TORNEOS = {
    "sin_ayudas": {
        "nombre": "Sin Ayudas",
        "desc": "No usar farmacos",
        "regla": "sin_farmacos",
        "duracion_dias": 7,
        "premio": {"dinero": 500, "titulo": "Purista"}
    },
    "speedrun": {
        "nombre": "Speed Run",
        "desc": "Cura rapido",
        "regla": "min_sesiones",
        "condicion": {"max_sesiones_extra": 0},
        "duracion_dias": 7,
        "premio": {"dinero": 400, "titulo": "Veloz"}
    },
    "hardcore": {
        "nombre": "Hardcore",
        "desc": "1 fallo = huye",
        "regla": "un_fallo_huye",
        "duracion_dias": 7,
        "premio": {"dinero": 600, "titulo": "Hardcore"}
    },
    "millonario": {
        "nombre": "Millonario",
        "desc": "Mas dinero gana",
        "regla": "ranking_dinero",
        "duracion_dias": 7,
        "premio": {"dinero": 300, "titulo": "Millonario"}
    },
    "pacifista": {
        "nombre": "Pacifista",
        "desc": "Sin farmacos agresivos",
        "regla": "sin_agresivos",
        "farmacos_prohibidos": ["electro", "lobo", "camisa"],
        "duracion_dias": 7,
        "premio": {"dinero": 350, "titulo": "Pacifista"}
    },
    "racha_master": {
        "nombre": "Racha Master",
        "desc": "Mejor racha gana",
        "regla": "ranking_racha",
        "duracion_dias": 7,
        "premio": {"dinero": 450, "titulo": "RachaMaster"}
    }
}


def iniciar_torneo(data, torneo_id):
    """Inicia un torneo"""
    if torneo_id not in TORNEOS:
        return False
    
    torneo = TORNEOS[torneo_id]
    data["torneo_activo"] = {
        "id": torneo_id,
        "nombre": torneo["nombre"],
        "regla": torneo["regla"],
        "dia_inicio": data["config"].get("ultimo_dia_jugado", ""),
        "stats": {
            "dinero_ganado": 0,
            "pacientes_curados": 0,
            "racha_max": 0,
            "farmacos_usados": [],
            "violaciones": 0
        }
    }
    return True


def registrar_accion_torneo(data, accion, valor=None):
    """Registra una acción para el torneo"""
    torneo = data.get("torneo_activo")
    if not torneo:
        return
    
    stats = torneo["stats"]
    
    if accion == "dinero":
        stats["dinero_ganado"] += valor
    elif accion == "curar":
        stats["pacientes_curados"] += 1
    elif accion == "racha":
        stats["racha_max"] = max(stats["racha_max"], valor)
    elif accion == "farmaco":
        stats["farmacos_usados"].append(valor)
        # Comprobar violación
        if torneo["regla"] == "sin_farmacos":
            stats["violaciones"] += 1
        elif torneo["regla"] == "sin_agresivos":
            prohibidos = TORNEOS[torneo["id"]].get("farmacos_prohibidos", [])
            if valor in prohibidos:
                stats["violaciones"] += 1


def finalizar_torneo(data):
    """Finaliza torneo y calcula resultado"""
    torneo = data.get("torneo_activo")
    if not torneo:
        return None
    
    torneo_def = TORNEOS.get(torneo["id"])
    stats = torneo["stats"]
    
    # Comprobar si ganó
    gano = stats["violaciones"] == 0
    
    if torneo["regla"] == "ranking_dinero":
        gano = stats["dinero_ganado"] >= 500  # Umbral
    elif torneo["regla"] == "ranking_racha":
        gano = stats["racha_max"] >= 15  # Umbral
    
    resultado = {
        "torneo": torneo["nombre"],
        "gano": gano,
        "stats": stats,
        "premio": torneo_def["premio"] if gano else None
    }
    
    data["torneo_activo"] = None
    return resultado


# ============================================================================
# REGALOS DE PACIENTES
# ============================================================================

REGALOS = {
    "carta": {
        "nombre": "Carta Agradecimiento",
        "probabilidad": 0.30,
        "efecto": {"reputacion": 5}
    },
    "bombones": {
        "nombre": "Caja de Bombones",
        "probabilidad": 0.20,
        "efecto": {"dinero": 50}
    },
    "recomendacion": {
        "nombre": "Recomendacion",
        "probabilidad": 0.15,
        "efecto": {"paciente_vip": True}
    },
    "objeto": {
        "nombre": "Objeto Misterioso",
        "probabilidad": 0.05,
        "efecto": {"item_aleatorio": True}
    },
    "flores": {
        "nombre": "Ramo de Flores",
        "probabilidad": 0.10,
        "efecto": {"reputacion": 3}
    },
    "vino": {
        "nombre": "Botella de Vino",
        "probabilidad": 0.08,
        "efecto": {"dinero": 75}
    },
    "denuncia": {
        "nombre": "Denuncia Falsa",
        "probabilidad": 0.10,
        "condicion": "muchos_farmacos",
        "efecto": {"reputacion": -20}
    },
    "nada": {
        "nombre": None,
        "probabilidad": 0.02,
        "efecto": {}
    }
}


def generar_regalo_paciente(data, paciente):
    """Genera regalo aleatorio de paciente curado"""
    farmacos_usados = len(paciente.get("farmacos_aplicados", []))
    
    # Probabilidad base de regalo
    prob_regalo = 0.3
    if paciente.get("tipo") == "vip":
        prob_regalo = 0.5
    
    if random.random() > prob_regalo:
        return None
    
    # Seleccionar regalo
    r = random.random()
    acumulado = 0
    
    for regalo_id, regalo in REGALOS.items():
        # Comprobar condición especial
        if regalo.get("condicion") == "muchos_farmacos" and farmacos_usados < 3:
            continue
        
        acumulado += regalo["probabilidad"]
        if r <= acumulado:
            if regalo["nombre"] is None:
                return None
            return {"id": regalo_id, "regalo": regalo}
    
    return None


def aplicar_regalo(data, regalo_info):
    """Aplica efectos de un regalo"""
    if not regalo_info:
        return
    
    efecto = regalo_info["regalo"]["efecto"]
    
    if "reputacion" in efecto:
        modificar_reputacion(data, efecto["reputacion"], "regalo")
    if "dinero" in efecto:
        from career_data import add_dinero
        add_dinero(data, efecto["dinero"])
    if efecto.get("paciente_vip"):
        # Marcar para próximo paciente VIP
        data["proximo_vip"] = True
    if efecto.get("item_aleatorio"):
        # Dar item aleatorio
        from career_data import CATALOGO_FARMACOS, add_item
        item = random.choice([f for f in CATALOGO_FARMACOS if not f.get("raro")])
        add_item(data, item["id"])


# ============================================================================
# PERSONALIZACIÓN
# ============================================================================

BATAS = {
    "clasica": {
        "nombre": "Bata Clasica",
        "desc": "Blanca y aburrida",
        "precio": 0,
        "requisito": None
    },
    "hawaiana": {
        "nombre": "Bata Hawaiana",
        "desc": "Flores tropicales",
        "precio": 200,
        "requisito": None
    },
    "cuero": {
        "nombre": "Bata de Cuero",
        "desc": "Muy profesional...",
        "precio": 500,
        "requisito": None
    },
    "manchada": {
        "nombre": "Bata Manchada",
        "desc": "Que son esas manchas?",
        "precio": 0,
        "requisito": {"logro": "carnicero"}
    },
    "dorada": {
        "nombre": "Bata Dorada",
        "desc": "Brilla como el oro",
        "precio": 0,
        "requisito": {"logro": "millonario"}
    },
    "camuflaje": {
        "nombre": "Bata Camuflaje",
        "desc": "Para esconderte",
        "precio": 350,
        "requisito": None
    },
    "pijama": {
        "nombre": "Pijama",
        "desc": "Comodo pero poco serio",
        "precio": 150,
        "requisito": None
    },
    "esmoquin": {
        "nombre": "Esmoquin Medico",
        "desc": "Elegancia ante todo",
        "precio": 800,
        "requisito": {"reputacion": 50}
    },
    "punk": {
        "nombre": "Bata Punk",
        "desc": "Con tachuelas",
        "precio": 400,
        "requisito": None
    },
    "invisible": {
        "nombre": "Bata Invisible",
        "desc": "... donde esta?",
        "precio": 0,
        "requisito": {"logro": "misterioso_curado"}
    }
}

DECORACIONES_EXTRA = {
    "pecera": {
        "nombre": "Pecera",
        "desc": "Relaja a pacientes",
        "precio": 400,
        "efecto": {"tolerancia": 1}
    },
    "poster_rock": {
        "nombre": "Poster de Rock",
        "desc": "AC/DC terapeutico",
        "precio": 150,
        "efecto": {}
    },
    "bola_plasma": {
        "nombre": "Bola de Plasma",
        "desc": "Hipnotizante",
        "precio": 250,
        "efecto": {"xp_mult": 1.05}
    },
    "mini_bar": {
        "nombre": "Mini Bar",
        "desc": "Para emergencias",
        "precio": 600,
        "efecto": {"dinero_mult": 1.05}
    },
    "estatua_freud": {
        "nombre": "Estatua de Freud",
        "desc": "Tamano real",
        "precio": 1000,
        "efecto": {"xp_mult": 1.1, "reputacion_bonus": 5}
    },
    "lampara_lava": {
        "nombre": "Lampara de Lava",
        "desc": "Muy sesentera",
        "precio": 200,
        "efecto": {}
    },
    "sillon_masaje": {
        "nombre": "Sillon Masaje",
        "desc": "Para ti, no pacientes",
        "precio": 800,
        "efecto": {"tolerancia": 1}
    },
    "neones": {
        "nombre": "Neones LED",
        "desc": "Ambiente de club",
        "precio": 300,
        "efecto": {}
    }
}


def get_batas_disponibles(data):
    """Obtiene batas disponibles para el jugador"""
    disponibles = []
    for bata_id, bata in BATAS.items():
        disponible = True
        req = bata.get("requisito")
        if req:
            if "logro" in req:
                if req["logro"] not in get_logros_desbloqueados(data):
                    disponible = False
            if "reputacion" in req:
                if get_reputacion(data) < req["reputacion"]:
                    disponible = False
        disponibles.append({
            "id": bata_id,
            "bata": bata,
            "disponible": disponible,
            "comprada": bata_id in data.get("batas_compradas", ["clasica"])
        })
    return disponibles


def comprar_bata(data, bata_id):
    """Compra una bata"""
    if bata_id not in BATAS:
        return False, "Bata no existe"
    
    bata = BATAS[bata_id]
    
    # Comprobar requisito
    req = bata.get("requisito")
    if req:
        if "logro" in req and req["logro"] not in get_logros_desbloqueados(data):
            return False, "Necesitas logro"
        if "reputacion" in req and get_reputacion(data) < req["reputacion"]:
            return False, "Falta reputacion"
    
    # Comprobar si ya la tiene
    if bata_id in data.get("batas_compradas", []):
        return False, "Ya la tienes"
    
    # Comprobar dinero
    from career_data import get_dinero, add_dinero
    if get_dinero(data) < bata["precio"]:
        return False, "Sin dinero"
    
    add_dinero(data, -bata["precio"])
    if "batas_compradas" not in data:
        data["batas_compradas"] = ["clasica"]
    data["batas_compradas"].append(bata_id)
    
    return True, "Comprada!"


def equipar_bata(data, bata_id):
    """Equipa una bata"""
    if bata_id not in data.get("batas_compradas", ["clasica"]):
        return False
    data["bata_equipada"] = bata_id
    return True


# ============================================================================
# PACIENTE ORÁCULO
# ============================================================================

FRASES_ORACULO = [
    "Veo nubes en tu futuro... o era un paciente fumador?",
    "El camello trae ofertas manana... o era pasado?",
    "Un VIP se acerca... o era un moroso?",
    "Los astros dicen que acertaras... o no",
    "Cuidado con el paciente de sombrero... no tiene sombrero",
    "Tu racha sera legendaria... si no fallas",
    "El dinero viene y va... sobre todo va",
    "Un familiar busca ayuda... o venganza",
    "Marte en Acuario significa... ni idea",
    "Las cartas revelan... que no se leer cartas",
    "Tu proxima opcion sera la B... o cualquier otra",
    "Siento una presencia... ah no, era hambre",
    "El universo conspira... para darte pacientes raros"
]

PREDICCIONES_ORACULO = [
    {"tipo": "evento", "texto": "Manana sera un dia especial..."},
    {"tipo": "paciente", "texto": "Alguien importante llegara pronto..."},
    {"tipo": "item", "regalo": True, "texto": "Toma esto, lo necesitaras..."},
    {"tipo": "dinero", "cantidad": 100, "texto": "El universo te recompensa..."},
    {"tipo": "advertencia", "texto": "Cuidado con las opciones obvias..."},
    {"tipo": "nada", "texto": "Hoy no veo nada claro... vuelve otro dia"}
]


def generar_visita_oraculo(data):
    """Genera visita del oráculo (cada 10 curados)"""
    curados = data["jugador"]["stats"].get("pacientes_curados", 0)
    ultima_visita = data.get("ultima_visita_oraculo", 0)
    
    if curados > 0 and curados % 10 == 0 and curados != ultima_visita:
        data["ultima_visita_oraculo"] = curados
        return True
    return False


def get_prediccion_oraculo():
    """Obtiene predicción aleatoria"""
    frase = random.choice(FRASES_ORACULO)
    prediccion = random.choice(PREDICCIONES_ORACULO)
    return {
        "frase": frase,
        "prediccion": prediccion
    }


def aplicar_prediccion_oraculo(data, prediccion):
    """Aplica efectos de la predicción"""
    pred = prediccion["prediccion"]
    
    if pred["tipo"] == "item" and pred.get("regalo"):
        from career_data import CATALOGO_FARMACOS, add_item
        item = random.choice([f for f in CATALOGO_FARMACOS if not f.get("raro")])
        add_item(data, item["id"])
        return f"Recibes: {item['nombre']}"
    elif pred["tipo"] == "dinero":
        from career_data import add_dinero
        add_dinero(data, pred["cantidad"])
        return f"Recibes: {pred['cantidad']}E"
    
    return pred["texto"]


# ============================================================================
# EVENTOS DE TEMPORADA
# ============================================================================

EVENTOS_TEMPORADA = {
    "navidad": {
        "nombre": "Depresion Navidena",
        "meses": [12],
        "dias": list(range(15, 32)),
        "efecto": {
            "todos_deprimidos": True,
            "item_especial": {
                "id": "prozac_navidad",
                "nombre": "Prozac Navideno",
                "desc": "+100% felicidad",
                "efecto": "mega_felicidad"
            }
        }
    },
    "halloween": {
        "nombre": "Noche de los Locos",
        "meses": [10],
        "dias": list(range(25, 32)),
        "efecto": {
            "pacientes_locos": True,
            "item_especial": {
                "id": "exorcismo",
                "nombre": "Exorcismo Light",
                "desc": "Saca demonios",
                "efecto": "cura_posesion"
            }
        }
    },
    "san_valentin": {
        "nombre": "Corazones Rotos",
        "meses": [2],
        "dias": list(range(10, 16)),
        "efecto": {
            "problemas_pareja": True,
            "item_especial": {
                "id": "filtro_amor",
                "nombre": "Filtro de Amor",
                "desc": "Paciente se enamora",
                "efecto": "enamoramiento"
            }
        }
    },
    "abril": {
        "nombre": "Dia de los Inocentes",
        "meses": [4],
        "dias": [1],
        "efecto": {
            "todo_alreves": True,
            "feedback_invertido": True
        }
    },
    "viernes13": {
        "nombre": "Viernes 13",
        "meses": list(range(1, 13)),
        "dias": [13],
        "condicion_extra": "viernes",
        "efecto": {
            "mala_suerte": True,
            "prob_huir_extra": 0.1
        }
    }
}


def check_evento_temporada(fecha_str):
    """Comprueba si hay evento de temporada activo"""
    # fecha_str formato: "DD/MM/YYYY" o similar
    try:
        partes = fecha_str.replace("-", "/").split("/")
        if len(partes) >= 2:
            dia = int(partes[0])
            mes = int(partes[1])
            
            for evento_id, evento in EVENTOS_TEMPORADA.items():
                if mes in evento["meses"] and dia in evento["dias"]:
                    return evento_id, evento
    except:
        pass
    return None, None


def get_item_temporada(evento_id):
    """Obtiene item especial de temporada si existe"""
    evento = EVENTOS_TEMPORADA.get(evento_id)
    if evento and "item_especial" in evento.get("efecto", {}):
        return evento["efecto"]["item_especial"]
    return None


# ============================================================================
# SISTEMA DE COMBOS
# ============================================================================

COMBOS = {
    "perfecto": {
        "nombre": "Perfecto!",
        "desc": "3 aciertos + curar",
        "condiciones": ["3_aciertos_seguidos", "curar"],
        "recompensa": {"dinero_mult": 1.5}
    },
    "farmaceutico": {
        "nombre": "Farmaceutico",
        "desc": "3 farmacos en 1 paciente",
        "condiciones": ["3_farmacos_paciente"],
        "recompensa": {"xp_mult": 1.3}
    },
    "speedster": {
        "nombre": "Speedster",
        "desc": "Curar en min sesiones",
        "condiciones": ["curar_minimo"],
        "recompensa": {"dinero": 100}
    },
    "drogata": {
        "nombre": "El Drogata",
        "desc": "Farmaco + 5 aciertos",
        "condiciones": ["usar_farmaco", "5_aciertos_seguidos"],
        "recompensa": {"item_gratis": True}
    },
    "intocable": {
        "nombre": "Intocable",
        "desc": "10 aciertos sin fallo",
        "condiciones": ["10_aciertos_seguidos"],
        "recompensa": {"dinero": 150, "reputacion": 5}
    },
    "combo_loco": {
        "nombre": "Combo Loco",
        "desc": "Curar 3 seguidos",
        "condiciones": ["3_curados_seguidos"],
        "recompensa": {"dinero": 200, "xp": 50}
    }
}


def check_combo(data, paciente, accion):
    """Comprueba si se activa un combo"""
    combos_activados = []
    stats = data["jugador"]["stats"]
    racha = stats.get("racha_aciertos_actual", 0)
    racha_curados = stats.get("racha_curados_actual", 0)
    
    if accion == "curar":
        # Combo perfecto
        if racha >= 3:
            combos_activados.append("perfecto")
        
        # Combo farmaceutico
        farmacos = len(paciente.get("farmacos_aplicados", []))
        if farmacos >= 3:
            combos_activados.append("farmaceutico")
        
        # Combo speedster
        if paciente["sesiones_completadas"] == paciente["sesiones_totales"]:
            # Curó en mínimas sesiones
            combos_activados.append("speedster")
        
        # Combo loco
        if racha_curados >= 3:
            combos_activados.append("combo_loco")
    
    if accion == "acierto":
        # Combo drogata
        if racha >= 5 and len(paciente.get("farmacos_aplicados", [])) > 0:
            combos_activados.append("drogata")
        
        # Combo intocable
        if racha >= 10:
            combos_activados.append("intocable")
    
    return combos_activados


def aplicar_combo(data, combo_id):
    """Aplica recompensas de un combo"""
    if combo_id not in COMBOS:
        return None
    
    combo = COMBOS[combo_id]
    recompensa = combo["recompensa"]
    resultado = {"combo": combo["nombre"], "efectos": []}
    
    if "dinero" in recompensa:
        from career_data import add_dinero
        add_dinero(data, recompensa["dinero"])
        resultado["efectos"].append(f"+{recompensa['dinero']}E")
    
    if "dinero_mult" in recompensa:
        resultado["dinero_mult"] = recompensa["dinero_mult"]
    
    if "xp_mult" in recompensa:
        resultado["xp_mult"] = recompensa["xp_mult"]
    
    if "xp" in recompensa:
        from career_data import add_xp
        add_xp(data, recompensa["xp"])
        resultado["efectos"].append(f"+{recompensa['xp']}XP")
    
    if "reputacion" in recompensa:
        modificar_reputacion(data, recompensa["reputacion"], "combo")
        resultado["efectos"].append(f"+{recompensa['reputacion']} Rep")
    
    if recompensa.get("item_gratis"):
        from career_data import CATALOGO_FARMACOS, add_item
        item = random.choice([f for f in CATALOGO_FARMACOS if not f.get("raro")])
        add_item(data, item["id"])
        resultado["efectos"].append(f"Item: {item['nombre']}")
    
    return resultado


# ============================================================================
# SISTEMA DE PRESTIGIO
# ============================================================================

PRESTIGIO_CONFIG = {
    "nivel_requerido": 20,
    "max_prestigios": 5,
    "bonus_por_prestigio": 0.10,  # +10% a todo
    "mantiene": ["logros", "titulos", "mejoras", "batas"],
    "pierde": ["dinero", "pacientes", "inventario", "nivel"]
}


def puede_prestigiar(data):
    """Comprueba si puede hacer prestigio"""
    nivel = data["jugador"].get("nivel", 1)
    prestigios = data.get("prestigio", {}).get("nivel", 0)
    
    if nivel < PRESTIGIO_CONFIG["nivel_requerido"]:
        return False, f"Necesitas nivel {PRESTIGIO_CONFIG['nivel_requerido']}"
    if prestigios >= PRESTIGIO_CONFIG["max_prestigios"]:
        return False, "Prestigio maximo alcanzado"
    
    return True, "OK"


def hacer_prestigio(data):
    """Realiza el prestigio"""
    puede, msg = puede_prestigiar(data)
    if not puede:
        return False, msg
    
    # Guardar lo que mantiene
    logros = data.get("logros", {}).copy()
    mejoras = data.get("mejoras", []).copy()
    batas = data.get("batas_compradas", ["clasica"]).copy()
    titulos = data["jugador"].get("titulos_disponibles", []).copy()
    prestigio_actual = data.get("prestigio", {}).get("nivel", 0)
    
    # Calcular nuevo prestigio
    nuevo_prestigio = prestigio_actual + 1
    bonus_total = nuevo_prestigio * PRESTIGIO_CONFIG["bonus_por_prestigio"]
    
    # Resetear datos
    data["jugador"]["nivel"] = 1
    data["jugador"]["xp"] = 0
    data["jugador"]["rango"] = "Becario"
    data["economia"]["dinero"] = 100
    data["inventario"] = []
    data["pacientes"] = []
    data["mensajes_pendientes"] = []
    
    # Restaurar lo que mantiene
    data["logros"] = logros
    data["mejoras"] = mejoras
    data["batas_compradas"] = batas
    data["jugador"]["titulos_disponibles"] = titulos
    
    # Establecer prestigio
    data["prestigio"] = {
        "nivel": nuevo_prestigio,
        "bonus": bonus_total,
        "estrellas": nuevo_prestigio
    }
    
    return True, {
        "nivel": nuevo_prestigio,
        "bonus": f"+{int(bonus_total * 100)}%",
        "estrellas": nuevo_prestigio
    }


def get_prestigio(data):
    """Obtiene info de prestigio actual"""
    return data.get("prestigio", {"nivel": 0, "bonus": 0, "estrellas": 0})


def get_bonus_prestigio(data):
    """Obtiene multiplicador de prestigio"""
    prestigio = get_prestigio(data)
    return 1.0 + prestigio.get("bonus", 0)


# ============================================================================
# NOTIFICACIONES INMERSIVAS
# ============================================================================

NOTIFICACIONES_INMERSIVAS = [
    "Doctor, tiene una llamada...",
    "Alguien pregunta por usted",
    "Su madre llamo. Dice que la llame.",
    "El Camello dejo un paquete",
    "Inspeccion de Sanidad manana...",
    "Un paciente pregunta si atiende mascotas",
    "Llego una carta certificada",
    "Hay alguien sospechoso en la sala",
    "Su ex pregunta si esta disponible",
    "El fontanero dice que vuelve manana",
    "Alguien dejo flores... sin tarjeta",
    "La policia quiere hablar con usted",
    "Un periodista quiere entrevistarle",
    "Su cuenta bancaria esta en negativo",
    "El vecino se queja del ruido",
    "Hay una furgoneta blanca fuera"
]


def get_notificacion_aleatoria():
    """Obtiene notificación inmersiva aleatoria"""
    return random.choice(NOTIFICACIONES_INMERSIVAS)
# Sistema de Apuestas


# ============================================================================
# SISTEMA DE APUESTAS - LA RULETA DEL LOCO
# ============================================================================

APUESTAS_CONFIG = {
    "minimo": 25,
    "maximo_fijo": 200,
    "maximo_porcentaje": 0.5,  # 50% del dinero
    "multiplicadores": {
        "acierto": 2.0,
        "racha_5": 3.0,
        "racha_10": 5.0
    }
}

LOGROS_APUESTAS = {
    "ludopata": {
        "nombre": "Ludopata",
        "desc": "Apuesta 50 veces",
        "condicion": ("apuestas_totales", ">=", 50),
        "recompensa": {"titulo": "Ludopata"}
    },
    "tahur": {
        "nombre": "El Tahur",
        "desc": "Gana 1000E apostando",
        "condicion": ("ganancias_apuestas", ">=", 1000),
        "recompensa": {"dinero": 200}
    },
    "arruinado": {
        "nombre": "Arruinado",
        "desc": "Pierde 500E apostando",
        "condicion": ("perdidas_apuestas", ">=", 500),
        "recompensa": {"titulo": "Arruinado"}
    },
    "suertudo": {
        "nombre": "Suertudo",
        "desc": "Gana 5 apuestas seguidas",
        "condicion": ("racha_apuestas_max", ">=", 5),
        "recompensa": {"dinero": 300}
    }
}


def puede_apostar(data, cantidad):
    """Comprueba si puede hacer una apuesta"""
    from career_data import get_dinero
    dinero = get_dinero(data)
    
    if cantidad < APUESTAS_CONFIG["minimo"]:
        return False, f"Minimo {APUESTAS_CONFIG['minimo']}E"
    
    max_permitido = min(
        APUESTAS_CONFIG["maximo_fijo"],
        int(dinero * APUESTAS_CONFIG["maximo_porcentaje"])
    )
    
    if cantidad > max_permitido:
        return False, f"Maximo {max_permitido}E"
    
    if cantidad > dinero:
        return False, "Sin dinero"
    
    return True, "OK"


def hacer_apuesta(data, cantidad):
    """Registra una apuesta antes de responder"""
    puede, msg = puede_apostar(data, cantidad)
    if not puede:
        return False, msg
    
    from career_data import add_dinero
    add_dinero(data, -cantidad)  # Quitar dinero
    
    data["apuesta_activa"] = {
        "cantidad": cantidad,
        "activa": True
    }
    
    # Stats
    if "apuestas" not in data:
        data["apuestas"] = {
            "totales": 0,
            "ganadas": 0,
            "perdidas": 0,
            "ganancias_total": 0,
            "perdidas_total": 0,
            "racha_actual": 0,
            "racha_max": 0
        }
    data["apuestas"]["totales"] += 1
    
    return True, "Apuesta registrada"


def resolver_apuesta(data, acierto, racha=0):
    """Resuelve la apuesta según resultado"""
    apuesta = data.get("apuesta_activa")
    if not apuesta or not apuesta.get("activa"):
        return None
    
    cantidad = apuesta["cantidad"]
    data["apuesta_activa"]["activa"] = False
    
    from career_data import add_dinero
    
    if acierto:
        # Calcular multiplicador
        if racha >= 10:
            mult = APUESTAS_CONFIG["multiplicadores"]["racha_10"]
        elif racha >= 5:
            mult = APUESTAS_CONFIG["multiplicadores"]["racha_5"]
        else:
            mult = APUESTAS_CONFIG["multiplicadores"]["acierto"]
        
        ganancia = int(cantidad * mult)
        add_dinero(data, ganancia)
        
        # Stats
        data["apuestas"]["ganadas"] += 1
        data["apuestas"]["ganancias_total"] += ganancia - cantidad
        data["apuestas"]["racha_actual"] += 1
        data["apuestas"]["racha_max"] = max(
            data["apuestas"]["racha_max"],
            data["apuestas"]["racha_actual"]
        )
        
        return {
            "resultado": "gano",
            "cantidad": cantidad,
            "ganancia": ganancia,
            "multiplicador": mult
        }
    else:
        # Pierde la apuesta
        data["apuestas"]["perdidas"] += 1
        data["apuestas"]["perdidas_total"] += cantidad
        data["apuestas"]["racha_actual"] = 0
        
        return {
            "resultado": "perdio",
            "cantidad": cantidad,
            "perdida": cantidad
        }


def get_apuesta_activa(data):
    """Obtiene apuesta activa si existe"""
    return data.get("apuesta_activa")


def get_stats_apuestas(data):
    """Obtiene estadísticas de apuestas"""
    return data.get("apuestas", {
        "totales": 0,
        "ganadas": 0,
        "perdidas": 0,
        "ganancias_total": 0,
        "perdidas_total": 0
    })


def get_max_apuesta(data):
    """Calcula máximo que puede apostar"""
    from career_data import get_dinero
    dinero = get_dinero(data)
    return min(
        APUESTAS_CONFIG["maximo_fijo"],
        int(dinero * APUESTAS_CONFIG["maximo_porcentaje"])
    )
