import os
import time
import threading
import asyncio
from bleak import BleakClient, discover
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler


UUID_CARACTERISTICA = "00002A37-0000-1000-8000-00805f9b34fb"
ARCHIVO_REGISTRO = "archivos_enviados.txt"  # Archivo para registrar archivos enviados

class ManejadorSincronizacion(FileSystemEventHandler):
    def __init__(self, carpeta_a_sincronizar, cliente):
        self.carpeta_a_sincronizar = carpeta_a_sincronizar
        self.cliente = cliente
        self.archivos_enviados = self.cargar_archivos_enviados()  # Carga los archivos enviados al inicio

    def on_modified(self, evento):
        if not evento.is_directory:
            # Llama a la función asincrónica para sincronizar el archivo
            asyncio.run(self.sincronizar_archivo(evento.src_path))

    async def sincronizar_archivo(self, ruta_archivo):
        try:
            # Verifico si el archivo ya ha sido enviado
            if not self.archivo_enviado(ruta_archivo):
                with open(ruta_archivo, 'rb') as f:
                    datos = f.read()
                    await self.cliente.write_gatt_char(UUID_CARACTERISTICA, datos)
                    print(f"Archivo enviado: {ruta_archivo}")
                    self.marcar_archivo_enviado(ruta_archivo)  #marco el archivo como enviado 
            else:
                print(f"El archivo ya fue enviado: {ruta_archivo}")
        except Exception as e:
            print(f"Error al enviar el archivo {ruta_archivo}: {e}")

    def archivo_enviado(self, ruta_archivo):
        # Verifico si el archivo yua ha sido enviado 
        return ruta_archivo in self.archivos_enviados

    def marcar_archivo_enviado(self, ruta_archivo):
        # Agregar el archivo a la lista de enviados y lo guarda en el archivo de registro
        self.archivos_enviados.add(ruta_archivo)
        with open(ARCHIVO_REGISTRO, 'a') as f:
            f.write(ruta_archivo + '\n')

    def cargar_archivos_enviados(self):
        # Carga los archivos enviados desde el archivo de registro
        if os.path.exists(ARCHIVO_REGISTRO):
            with open(ARCHIVO_REGISTRO, 'r') as f:
                return set(line.strip() for line in f)
        return set()

async def monitorear_carpeta(carpeta_a_sincronizar, cliente):
    manejador = ManejadorSincronizacion(carpeta_a_sincronizar, cliente)
    observador = Observer()
    observador.schedule(manejador, carpeta_a_sincronizar, recursive=True)
    observador.start()
    
    try:
        while True:
            await asyncio.sleep(1)  # Mantener el hilo activo sin bloquear
    except KeyboardInterrupt:
        observador.stop()
    observador.join()

async def main():
    try:
        print("[!] Escaneando dispositivos Bluetooth...")
        dispositivos = await discover()
        print("Dispositivos encontrados:", dispositivos)

        # Dirección MAC del dispositivo receptor 
        direccion_objetivo = input("Ingrese la dirección MAC del dispositivo receptor: ")

        async with BleakClient(direccion_objetivo) as cliente:
            carpeta_a_sincronizar = input("Ingrese la ruta de la carpeta para sincronizar: ")
            # Inicia el monitoreo en un hilo separado
            hilo_sincronizacion = threading.Thread(target=monitorear_carpeta, args=(carpeta_a_sincronizar, cliente))
            hilo_sincronizacion.start()

            # Mantiene el programa en ejecución mientras se monitorea la carpeta
            while hilo_sincronizacion.is_alive():
                await asyncio.sleep(1)

    except Exception as e:
        print(f"Ocurrió un error: {e}")

if __name__ == "__main__":
    asyncio.run(main())

