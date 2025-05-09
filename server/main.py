# servidor/main.py

import Pyro5.api
from juego import Juego

SERVER_HOST = "127.0.0.1"
NS_PORT = 4002

def main():
    # 1) Arrancar el daemon en localhost, puerto dinámico
    daemon = Pyro5.api.Daemon(host=SERVER_HOST, port=0)
    
    # 2) Crear la instancia de Juego
    juego = Juego()
    
    # 3) Registrar el objeto Juego en el daemon
    uri = daemon.register(juego)
    
    # 4) Conectar al NameServer y registrar el nombre "Juego"
    ns = Pyro5.api.locate_ns(host=SERVER_HOST, port=NS_PORT)
    ns.register("Juego", uri)
    
    print(f"[SERVIDOR] Juego registrado como 'Juego' en {uri}")
    print(f"[SERVIDOR] Esperando llamadas de clientes…")
    
    # 5) Entrar al bucle de servicio
    daemon.requestLoop()

if __name__ == "__main__":
    main()
