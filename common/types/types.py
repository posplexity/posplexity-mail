from pydantic import BaseModel
from datetime import datetime

class OfflineEvent(BaseModel):
    subject: str
    title: str
    date: datetime
    location: str

class OnlineEvent(BaseModel):
    subject: str
    title: str
    date: datetime
    url: str

class Mail(BaseModel):
    subject: str
    summary: str
    sender: str
    date_received: str
    offline_events: list[OfflineEvent]=[]
    online_events: list[OnlineEvent]=[]