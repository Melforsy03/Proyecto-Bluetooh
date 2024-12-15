import os
import time
import threading
from bleak import BleakClient, discover
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

UUID_CARACTERISTICA = "00002A37-0000-1000-8000-00805f9b34fb" 

class ManejadorSincronizacion(FileSystemEventHandler):
    def __init__(self, carpeta_a_sincronizar, cliente):
        self.carpeta_a_sincronizar = carpeta_a_sincronizar
        self.cliente = cliente

    def on_modified(self, evento):
        if not evento.is_directory:
            # Llama a la función asincrónica para sincronizar el archivo
            asyncio.run(self.sincronizar_archivo(evento.src_path))

    async def sincronizar_archivo(self, ruta_archivo):
        # Envía el archivo a través de BLE
        with open(ruta_archivo, 'rb') as f:
            datos = f.read()
            await self.cliente.write_gatt_char(UUID_CARACTERISTICA, datos)
            print(f"Archivo enviado: {ruta_archivo}")

async def monitorear_carpeta(carpeta_a_sincronizar, cliente):
    manejador = ManejadorSincronizacion(carpeta_a_sincronizar, cliente)
    observador = Observer()
    observador.schedule(manejador, carpeta_a_sincronizar, recursive=True)
    observador.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observador.stop()
    observador.join()

async def main():

    dispositivos = await discover()

    # dirección MAC del dispositivo receptor
    direccion_objetivo = 'XX:XX:XX:XX:XX:XX' 

    async with BleakClient(direccion_objetivo) as cliente:
        carpeta_a_sincronizar = input("Ingresar la ruta de la carpeta para sincronizar: ")
        # Inicia el monitoreo en un hilo separado
        hilo_sincronizacion = threading.Thread(target=monitorear_carpeta, args=(carpeta_a_sincronizar, cliente))
        hilo_sincronizacion.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
