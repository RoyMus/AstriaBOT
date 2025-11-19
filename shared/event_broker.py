"""
Event broker for inter-service communication using Azure Service Bus
"""
import json
import logging
from abc import ABC, abstractmethod
from azure.messaging.servicebus import ServiceBusClient, ServiceBusMessage
from azure.identity import DefaultAzureCredential
from pydantic import BaseModel
from typing import Callable, Coroutine, Any
import os


class Event(BaseModel):
    """Base event model"""
    event_type: str
    data: dict
    timestamp: str
    source_service: str


class EventPublisher(ABC):
    """Abstract event publisher"""
    
    @abstractmethod
    async def publish(self, event: Event) -> None:
        pass


class EventSubscriber(ABC):
    """Abstract event subscriber"""
    
    @abstractmethod
    async def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        pass


class ServiceBusEventBroker(EventPublisher, EventSubscriber):
    """Azure Service Bus implementation for event brokering"""
    
    def __init__(self, connection_string: str = None):
        if connection_string is None:
            connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
        
        if not connection_string:
            raise ValueError("SERVICEBUS_CONNECTION_STRING not configured")
        
        self.connection_string = connection_string
        self.client = ServiceBusClient.from_connection_string(connection_string)
        self.handlers = {}
    
    async def publish(self, event: Event) -> None:
        """Publish event to topic"""
        try:
            topic_name = f"events-{event.event_type}"
            sender = self.client.get_topic_sender(topic_name)
            
            message = ServiceBusMessage(
                body=event.model_dump_json(),
                subject=event.event_type,
                content_type="application/json"
            )
            
            with sender:
                sender.send_messages(message)
            
            logging.info(f"Published event: {event.event_type}")
        except Exception as e:
            logging.error(f"Failed to publish event: {e}")
            raise
    
    async def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        """Subscribe to events of a specific type"""
        topic_name = f"events-{event_type}"
        self.handlers[event_type] = (topic_name, handler)
        logging.info(f"Subscribed to {event_type}")
    
    async def start_listener(self, event_type: str, subscription_name: str) -> None:
        """Start listening for events"""
        if event_type not in self.handlers:
            logging.warning(f"No handler registered for {event_type}")
            return
        
        topic_name, handler = self.handlers[event_type]
        
        try:
            receiver = self.client.get_subscription_receiver(topic_name, subscription_name)
            
            with receiver:
                for msg in receiver:
                    try:
                        event_data = json.loads(str(msg))
                        event = Event(**event_data)
                        await handler(event)
                        msg.complete()
                    except Exception as e:
                        logging.error(f"Failed to process message: {e}")
                        msg.dead_letter()
        except Exception as e:
            logging.error(f"Listener failed for {event_type}: {e}")
            raise


class LocalEventBroker(EventPublisher, EventSubscriber):
    """Local in-memory event broker for development"""
    
    def __init__(self):
        self.handlers = {}
        self.events = []
    
    async def publish(self, event: Event) -> None:
        """Publish event locally"""
        self.events.append(event)
        
        if event.event_type in self.handlers:
            handler = self.handlers[event.event_type]
            await handler(event)
        
        logging.info(f"Published event locally: {event.event_type}")
    
    async def subscribe(self, event_type: str, handler: Callable[[Event], Coroutine]) -> None:
        """Subscribe to events"""
        self.handlers[event_type] = handler
        logging.info(f"Subscribed locally to {event_type}")


# Factory function
def get_event_broker() -> EventPublisher:
    """Get appropriate event broker based on environment"""
    env = os.getenv("ENVIRONMENT", "development")
    
    if env == "production":
        connection_string = os.getenv("SERVICEBUS_CONNECTION_STRING")
        return ServiceBusEventBroker(connection_string)
    else:
        return LocalEventBroker()


# Common event types
class UserMessageReceivedEvent(Event):
    event_type = "user_message_received"


class ImageProcessedEvent(Event):
    event_type = "image_processed"


class PaymentReceivedEvent(Event):
    event_type = "payment_received"


class TuneCreatedEvent(Event):
    event_type = "tune_created"


class PackImagesUpdatedEvent(Event):
    event_type = "pack_images_updated"
