from dataclasses import dataclass
from typing import Any

@dataclass
class A2AMessage:
    sender: str
    receiver: str
    intent: str
    domain: str
    query: str
    payload: dict = None

@dataclass  
class A2AResponse:
    sender: str
    receiver: str
    status: str
    result: Any

def send_message(message: A2AMessage, agent_registry: dict) -> A2AResponse:
    receiver = agent_registry.get(message.receiver)
    if not receiver:
        return A2AResponse(
            sender="system",
            receiver=message.sender,
            status="error",
            result=f"Agent {message.receiver} not found"
        )
    result = receiver(message)
    return A2AResponse(
        sender=message.receiver,
        receiver=message.sender,
        status="success",
        result=result
    )