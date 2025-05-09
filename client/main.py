import Pyro5.api
import threading
import time
import sys

SERVER_HOST = "127.0.0.1"
NS_PORT = 4002
SALIR = "SALIR"

@Pyro5.api.expose
class Jugador:
    def __init__(self, nombre, uri_juego):
        self.nombre = nombre
        self.uri_juego = uri_juego  # para posteriores llamadas si necesitas

    def notificacion(self, mensaje):
        print(f"\n[NOTIFICACIÓN] {mensaje}")

    def solicitar_votacion(self, nuevo_nombre):
        print(f"\n[DECISIÓN] ¿Aceptar a {nuevo_nombre} en tu equipo? (s/n)")
        decision = input("Tu decisión > ").strip().lower()
        return decision == "s"

def escuchar_notificaciones(jugador, daemon, uri):
    ns = Pyro5.api.locate_ns(host="127.0.0.1", port=4002)
    ns.register("cliente.jugador." + jugador.nombre, uri)
    print(f"[CLIENTE] Registrado como cliente.jugador.{jugador.nombre}")
    daemon.requestLoop()

def main():
    if len(sys.argv) != 3:
        print("Uso: python main.py <nombre_jugador> <nombre_equipo>")
        sys.exit(1)

    nombre = sys.argv[1]
    equipo = sys.argv[2]

    # 1) Conectarnos al NameServer
    ns = Pyro5.api.locate_ns(host=SERVER_HOST, port=NS_PORT)
    uri_juego = ns.lookup("Juego")
    juego = Pyro5.api.Proxy(uri_juego)

    # 2) Crear nuestro objeto Jugador y exponerlo
    jugador = Jugador(nombre, uri_juego)
    daemon = Pyro5.api.Daemon(host="127.0.0.1", port=0)
    uri_jugador = daemon.register(jugador)

    # 3) Registro AUTOMÁTICO al servidor de juego
    respuesta = juego.registrar_jugador(nombre, equipo)
    print(f"[JUEGO] {respuesta}")

    # 4) Arrancar hilo de notificaciones
    hilo = threading.Thread(target=escuchar_notificaciones, args=(jugador, daemon, uri_jugador), daemon=True)
    hilo.start()

    # 5) Menú de acciones
    try:
        while True:
            print("\nOpciones:")
            print("0. Iniciar juego")
            print("1. Lanzar dado")
            print("2. Ver estado del juego")
            print("3. Salir")

            opcion = input("Selecciona una opción: ").strip()
            if opcion == "0":
                print(juego.iniciar_juego())
            elif opcion == "1":
                resultado = juego.lanzar_dado(equipo)
                print(f"[JUEGO] {resultado}")
            elif opcion == "2":
                estado = juego.obtener_estado()
                print(f"[ESTADO]\n{estado}")
            elif opcion == "3" or opcion.upper() == SALIR:
                print("Saliendo...")
                break
            else:
                print("Opción no válida.")
            time.sleep(0.5)
    except KeyboardInterrupt:
        print("\nCliente interrumpido.")

    # 6) Mantenemos el daemon activo para recibir notificaciones
    daemon.requestLoop()

if __name__ == "__main__":
    main()
