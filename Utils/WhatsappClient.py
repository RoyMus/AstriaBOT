import uuid
from Utils import constants
import aiohttp

def process_incoming_messages(data):
    transformed_messages = []
    for entry in data.get("entry", []):
        for change in entry.get("changes", []):
            if change["value"]["metadata"]["phone_number_id"] != constants.WHATSAPP_NUMBER_ID:
                return transformed_messages
            message_data = change.get("value", {}).get("messages", [])
            for message in message_data:
                # Generate a unique message ID
                message_sid = message.get("id", str(uuid.uuid4()))
                if message.get("errors"):
                    # If there's an error in the message, skip processing
                    continue
                # Extract sender's phone number
                from_number = message.get("from", "Unknown")

                # Extract text message (if exists)
                body = message.get("text", {}).get("body", "")
                # Count media attachments
                media_types = ["image", "text", "interactive"]
                invalid_media = False
                if message.get("type") not in media_types:
                    invalid_media = True
               
                interactive_reply = message.get("interactive",None)
                button_pressed = None
                list_item_pressed = None
                if interactive_reply and interactive_reply["type"] == "button_reply":
                    button_pressed = interactive_reply["button_reply"]
                if interactive_reply and interactive_reply["type"] == "list_reply":
                    list_item_pressed = interactive_reply["list_reply"]
                # Extract media URLs if present
                media_urls = []
                media_types = ["image"]
                num_media = sum(1 for media in media_types if media in message)

                for index, media in enumerate(media_types):
                    if media in message:
                        media_id = message.get(media)
                        if media_id:
                            media_id = media_id.get("id")
                            if media_id:
                                media_urls.append(
                                    (f"MediaID{index}", media_id)
                                )

                # Twilio-like transformed request format
                transformed_message = {
                    "SmsMessageSid": message_sid,
                    "NumMedia": str(num_media),
                    "From": from_number,
                    "Body": body,
                    "InvalidMedia": invalid_media,
                }
                # Add media URLs if available
                transformed_message.update(dict(media_urls))
                transformed_messages.append(transformed_message)
                if button_pressed:
                    transformed_message["reply"] = button_pressed
                if list_item_pressed:
                    transformed_message["list_reply"] = list_item_pressed
    return transformed_messages


class WhatsappClient:
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {constants.WHATSAPP_API_KEY}"
        }

    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    async def send_typing_indicator(self, client_number: str,message_id:str):
        data = {
            "messaging_product": "whatsapp",
            "status":"read",
            "message_id": message_id,
            "typing_indicator": {
                "type": "text",
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def send_image_to_client(self, client_number: str, image_url: str, message_body: str = None):
        data = {
            "messaging_product": "whatsapp",
            "to": client_number,
            "type": "image",
            "image": {
                "link": image_url,
                "caption": message_body
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def send_image_to_client_using_id(self, client_number: str, image_id: int, message_body: str = None):
        data = {
            "messaging_product": "whatsapp",
            "to": client_number,
            "type": "image",
            "image": {
                "id": image_id,
                "caption": message_body
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def reply_to_message(self, client_number: str, message_body: str, message_id: str):
        data = {
            "messaging_product": "whatsapp",
            "to": client_number,
            "type": "text",
            "text": {
                "body": message_body
            },
            "context": {
                "message_id": message_id
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result

    async def send_interactive_reply_image(self, client_number: str, image_url: str, message_body: str,button_id:int,button_text:str,additional_button_id:str=None,additional_button_text:str=None):
        data = {
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": client_number,
          "type": "interactive",
          "interactive": {
            "type": "button",
            "header": {
                "type":"image",
                "image": {
                    "link": image_url,
                }
            },
            "body": {
              "text": message_body
            },
            "footer": {
              "text": ""
            },
            "action": {
              "buttons": [
                {
                  "type": "reply",
                  "reply": {
                    "id": button_id,
                    "title": button_text
                  }
                },
                ({
                    "type": "reply",
                    "reply": {
                        "id": additional_button_id,
                        "title": additional_button_text
                    }
                }) if additional_button_id and additional_button_text else None
              ]
            }
          }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def send_interactive_reply_message(self, client_number: str, message_body: str,button_id:int,button_text:str, title:str,additional_button_id:int=None,additional_button_text:str=None):
        data = {
          "messaging_product": "whatsapp",
          "recipient_type": "individual",
          "to": client_number,
          "type": "interactive",
          "interactive": {
            "type": "button",
            "header": {
                "type": "text",
                "text": title
            },
            "body": {
              "text": message_body
            },
            "footer": {
              "text": ""
            },
            "action": {
              "buttons": [
                {
                  "type": "reply",
                  "reply": {
                    "id": button_id,
                    "title": button_text
                  }
                },
                
                ({
                    "type": "reply",
                    "reply": {
                        "id": additional_button_id,
                        "title": additional_button_text
                    }
                }) if additional_button_id and additional_button_text else None
              ]
            }
          }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def send_interactive_url(self,client_number:str,header_text:str,message_body:str,footer_text:str,url_button_text:str,url_link:str):
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client_number,
            "type": "interactive",
            "interactive": {
                "type": "cta_url",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": message_body
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "name": "cta_url",
                    "parameters": {
                        "display_text": url_button_text,
                        "url": url_link
                    }
                }
            }
       }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
   
    async def send_interactive_list_message(self, client_number: str, header_text: str, message_body: str,footer_text:str, button_text: str, options: dict):
        # Dynamically create rows based on the options list
        rows = [{"id": key, "title": value} for key, value in options.items()]

        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client_number,
            "type": "interactive",
            "interactive": {
                "type": "list",
                "header": {
                    "type": "text",
                    "text": header_text
                },
                "body": {
                    "text": message_body
                },
                "footer": {
                    "text": footer_text
                },
                "action": {
                    "button": button_text,
                    "sections": [
                        {
                            "title": "Select your option",
                            "rows": rows
                        }
                    ]
                }
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result

    async def send_message_to_client(self, client_number: str, message_body: str):
        # Send a response message back to the sender
        data = {
            "messaging_product": "whatsapp",
            "to": client_number,
            "recipient_type": "individual",
            "text":
                {
                    "body": message_body
                }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    
    async def send_reaction_message(self, client_number: str, message_id: str, emoji:str):
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": f"{client_number}",
            "type": "reaction",
            "reaction": {
                "message_id": f"{message_id}",
                "emoji": f"{emoji}"
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    async def send_whatsapp_video(self, client_number: str, video_url: str, message_body: str = None):
        data = {
            "messaging_product": "whatsapp",
            "recipient_type": "individual",
            "to": client_number,
            "type": "video",
            "video": {
                "link": video_url,
                "caption": message_body
            }
        }
        response = await self.session.post(f"{constants.WHATSAPP_API_URL}/{constants.WHATSAPP_NUMBER_ID}/messages", headers=self.headers, json=data)
        result = await response.json()
        return result
    
    async def get_whatsapp_image(self, media_id: int):
        # Send a response message back to the sender
        response = await self.session.get(f"{constants.WHATSAPP_API_URL}/{media_id}", headers=self.headers)
        response = await response.json()
        image_url = response.get("url")
        image_response = await self.session.get(image_url, headers=self.headers)
        image_data = await image_response.read()
        return image_data


