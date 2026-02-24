# # from channels.generic.websocket import AsyncWebsocketConsumer
# # import json

# # class AdminNotificationConsumer(AsyncWebsocketConsumer):
# #     async def connect(self):
# #         await self.channel_layer.group_add("admins", self.channel_name)
# #         await self.accept()

# #     async def disconnect(self, close_code):
# #         await self.channel_layer.group_discard("admins", self.channel_name)

# #     async def send_notification(self, event):
# #         await self.send(text_data=json.dumps(event["message"]))
from channels.generic.websocket import AsyncWebsocketConsumer
import json

# class AdminNotificationConsumer(AsyncWebsocketConsumer):

#     async def connect(self):
#         self.group_name = "admins"   # 👈 SAME NAME EVERYWHERE

#         await self.channel_layer.group_add(
#             self.group_name,
#             self.channel_name
#         )

#         await self.accept()

#     async def disconnect(self, close_code):
#         await self.channel_layer.group_discard(
#             self.group_name,
#             self.channel_name
#         )

#     async def send_notification(self, event):
#         await self.send(text_data=json.dumps(event["data"]))  # 👈 use "data"
# orders/consumers.py
class AdminNotificationConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        try:
            print("🔥 WebSocket connect called")

            self.group_name = "admins"

            await self.channel_layer.group_add(
                self.group_name,
                self.channel_name
            )

            await self.accept()

            print("✅ WebSocket accepted")

        except Exception as e:
            print("❌ CONNECT ERROR:", str(e))

    async def send_notification(self, event):
        try:
            print("📨 Sending notification:", event)
            await self.send(text_data=json.dumps(event["data"]))
        except Exception as e:
            print("❌ SEND ERROR:", str(e))