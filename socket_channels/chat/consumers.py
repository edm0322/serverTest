import json
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

class CommandConsumer(AsyncWebsocketConsumer):
    connected_clients = set()  # 클래스 변수로 정의

    @classmethod
    async def get_clients(cls):
        return cls.connected_clients

    @classmethod
    async def add_client(cls, client_id):
        cls.connected_clients.add(client_id)

    @classmethod
    async def remove_client(cls, client_id):
        cls.connected_clients.remove(client_id)

    async def connect(self):
        await self.accept()
        self.client_id = self.scope['client'][0]
        await self.channel_layer.group_add("command_group", self.channel_name)
        await self.add_client(self.client_id)
        await self.update_client_list()
        print(f"Client connected: {self.client_id}")

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard("command_group", self.channel_name)
        await self.remove_client(self.client_id)
        await self.update_client_list()
        print(f"Client disconnected: {self.client_id}")

    async def receive(self, text_data):
        print(f"Received message: {text_data}")
        data = json.loads(text_data)
        message_type = data.get('type')
        
        if message_type == 'command_request':
            command = data.get('command')
            target_client = data.get('target_client')
            if target_client == 'all':
                await self.send_command_to_all(command)
            else:
                await self.send_command_to_client(target_client, command)

        elif message_type == "command_result":
            data['client_id'] = self.client_id
            await self.broadcast_result(data)
            
    async def send_command_to_all(self, command):
        clients = await self.get_clients()
        for client in clients:
            if client != '127.0.0.1' and client != "localhost":
                await self.channel_layer.group_send(
                    "command_group",
                    {
                        "type" : "send_command",
                        "target_client" : client,
                        "command" : command
                    }
                )
    
    async def send_command_to_client(self, target_client, command):
        await self.channel_layer.group_send(
            "command_group",
            {
                "type": "send_command",
                "target_client" : target_client,
                "command": command
            }
        )

    async def send_command(self, event):
        if event['target_client'] == self.client_id:
            await self.send(text_data = json.dumps({
                'type' : 'execute_command',
                'command' : event['command']
            }))

    async def broadcast_result(self, data):
        await self.channel_layer.group_send(
            "command_group",
            {
                "type": "client_command_result",
                "client_id" : data['client_id'],
                "command": data["command"],
                "result": data["result"]
            }
        )

    async def update_client_list(self):
        clients = await self.get_clients()
        client_count = len([c for c in clients if c not in ("127.0.0.1", "localhost")])
        await self.channel_layer.group_send(
            "command_group",
            {
                "type": "client_list_update",
                "clients": list(clients),
                "client_count": client_count
            }
        )

    async def client_list_update(self, event):
        await self.send(text_data=json.dumps({
            'type': 'client_list_update',
            'clients': event['clients'],
            "client_count": event['client_count']
        }))
