from pydantic import BaseModel
from datetime import datetime

class OfflineEvent(BaseModel):
    subject: str
    title: str
    start_datetime: datetime
    end_datetime: datetime=None
    location: str
    explanation: str

class OnlineEvent(BaseModel):
    subject: str
    title: str
    start_datetime: datetime
    end_datetime: datetime=None
    url: str
    explanation: str

class Events(BaseModel):
    offline_events: list[OfflineEvent]
    online_events: list[OnlineEvent]

class Mail(BaseModel):
    subject: str
    summary: str
    sender: str
    date_received: str
    events: Events=None