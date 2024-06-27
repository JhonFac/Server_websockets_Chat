import asyncio
import websockets
import json

clients = []  # Lista para almacenar los clientes conectados

# Función para difundir la lista de clientes conectados
async def broadcast_clients_list():
    clients_list = [client['name_user'] for client in clients]
    message = json.dumps({'event': 'list_users', 'users': clients_list})
    for client in clients:
        try:
            await client['websocket'].send(message)
        except websockets.exceptions.ConnectionClosedError:
            pass  # Ignorar clientes que se desconectaron

async def handler(websocket, path):
    global clients

    # Recibir el nombre del cliente desde el cliente web
    data = await websocket.recv()
    data = json.loads(data)
    clients.append({"name_user": data['name'], "websocket": websocket})
    print(f"Nuevo cliente conectado: {data['name']}")
    # print(f"Lista de clientes: {clients}")

    # Enviar la lista de clientes conectados a todos
    await broadcast_clients_list()

    try:
        while True:
            # Esperar mensajes del cliente web y procesarlos
            message_json = await websocket.recv()
            message_data = json.loads(message_json)
            print(message_data)
            recipient_name = message_data.get('recipient', None)
            if recipient_name:
                # Buscar al destinatario en la lista de clientes
                recipient = next((client for client in clients if client['name_user'] == recipient_name), None)
                if recipient:
                    recipient_websocket = recipient['websocket']
                    await recipient_websocket.send(message_json)
                else:
                    print(f"No se encontró al destinatario {recipient_name}.")
            else:
                print("Mensaje no tiene destinatario especificado.")
    
    except websockets.exceptions.ConnectionClosedError:
        print(f"Cliente {data['name']} desconectado.")
    except websockets.exceptions.ConnectionClosedOK:
        print(f"Cliente {data['name']} desconectado (ClosedOK).")
    finally:
        clients = [client for client in clients if client['websocket'] != websocket]
        # print(f"Cliente {data['name']} eliminado de la lista de clientes.")
        await broadcast_clients_list()  # Actualizar lista de clientes conectados

async def main():
    async with websockets.serve(handler, "localhost", 8765):
        print("Servidor de WebSockets levantado y escuchando en ws://localhost:8765")
        await asyncio.Future()  # Mantener el servidor en ejecución

if __name__ == "__main__":
    asyncio.run(main())



# {'user': 'Willam', 'messages': [
#     {'Jhon': [
#         {'received': 'hola', 'date': datetime} <- lo recibio de Jhon 
#         {'sended': 'hola como estas', 'date': datetime} <- lo envio William
#         {'sended': 'que haces', 'date': datetime} <- lo envio William
#         {'sended': 'como te a ido', 'date': datetime} <- lo envio William
#         {'received': 'bien y tu.?', 'date': datetime} <- lo recibio de Jhon
#     ]
#     },
#     {'Lorena': [
#         {'received': 'hola', 'date': datetime} <- lo recibio de Lorena
#         {'sended': 'hola como estas', 'date': datetime} <- lo envio William
#         {'sended': 'que haces', 'date': datetime} <- lo envio William
#         {'sended': 'como te a ido', 'date': datetime} <- lo envio William
#         {'received': 'bien y tu.?', 'date': datetime} <- lo recibio de Lorena
#     ]
#     }
# .
# .
# .
# ]
# }