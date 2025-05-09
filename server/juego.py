import Pyro5.api
import random
import json
import os

@Pyro5.api.expose
class Juego:
    def __init__(self):
        # Leer configuración
        with open(os.path.join(os.path.dirname(__file__), "config.json")) as f:
            config = json.load(f)

        # Aplicar configuración
        self.tablero_max = config.get("tablero_size", 100)
        self.dado_min = config.get("dado_min", 1)
        self.dado_max = config.get("dado_max", 6)

        # Inicializar equipos por defecto
        self.equipos = {nombre: [] for nombre in config.get("equipos_por_defecto", [])}

        self.orden_turnos = []
        self.indice_turno = 0
        self.posiciones = {}
        

    def registrar_jugador(self, nombre_jugador, nombre_equipo):
        if nombre_equipo not in self.equipos:
            self.equipos[nombre_equipo] = []
        if nombre_jugador not in self.equipos[nombre_equipo]:
            self.equipos[nombre_equipo].append(nombre_jugador)
        return f"Jugador {nombre_jugador} registrado en equipo {nombre_equipo}."

    def obtener_estado(self):
        if not self.equipos:
            return "No hay jugadores registrados aún."
        estado = ""
        for eq, jugs in self.equipos.items():
            estado += f"{eq}: {', '.join(jugs)}\n"
        return estado.strip()

    def iniciar_juego(self):
        if self.orden_turnos:  # ya se inició
            return "El juego ya está en curso."
        if len(self.equipos) < 2:
            return "Se necesitan al menos dos equipos."
        
        self.orden_turnos = list(self.equipos.keys())
        random.shuffle(self.orden_turnos)
        self.indice_turno = 0
        self.posiciones = {eq: 0 for eq in self.equipos}
        
        return f"Juego iniciado. Orden de turnos: {self.orden_turnos}"

    def turno_actual(self):
        if not self.orden_turnos:
            return "Juego no iniciado."
        return self.orden_turnos[self.indice_turno]

    def lanzar_dado(self, nombre_equipo):
        if not self.orden_turnos:
            return "Juego no iniciado."
        equipo = self.orden_turnos[self.indice_turno]
        if equipo != nombre_equipo:
            return f"No es el turno de {nombre_equipo}, es turno de {equipo}."
        # cada jugador suma un dado
        total = sum(random.randint(self.dado_min, self.dado_max) for _ in self.equipos[equipo])
        self.posiciones[equipo] += total
        resultado = f"{equipo} avanza {total} (total {self.posiciones[equipo]})"
        # verificar victoria
        if self.posiciones[equipo] >= self.tablero_max:
            # reset orden para que no siga activo
            self.orden_turnos = []
            return resultado + f" → ¡{equipo} gana!"
        # pasar al siguiente turno
        self.indice_turno = (self.indice_turno + 1) % len(self.orden_turnos)
        return resultado