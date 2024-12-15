import asyncio
from bleak import BleakClient, discover


UUID_CARACTERISTICA = "00002A37-0000-1000-8000-00805f9b34fb"  

# Función que se llama cuando se recibe una notificación
def notificacion_callback(datos):
    # Guarda los datos recibidos en un archivo
    with open('archivo_recibido', 'wb') as f:
        f.write(datos)
    print("Archivo recibido y guardado como 'archivo_recibido'.")

async def conectar_y_recibir(direccion_objetivo):
    async with BleakClient(direccion_objetivo) as cliente:
        print(f"Conectado a {direccion_objetivo}")
        # Configura la notificación para la característica
        await cliente.start_notify(UUID_CARACTERISTICA, notificacion_callback)
        # Mantén la conexión abierta para recibir notificaciones
        while True:
            await asyncio.sleep(1)

async def main():
    dispositivos = await discover()
    print("Dispositivos encontrados:", dispositivos)
    
    #  dirección MAC del dispositivo emisor
    direccion_objetivo = 'XX:XX:XX:XX:XX:XX' 

    await conectar_y_recibir(direccion_objetivo)

if __name__ == "__main__":
    asyncio.run(main())
