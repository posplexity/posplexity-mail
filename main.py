import datetime

from src.fetch import fetch_mails_from_apple_mail
from src.extract import extract_events
from src.utils.utils import parse_mail


def main():
    # 1. Fetch & Parse Mails
    mails = [
        parse_mail(mail) 
        for mail in fetch_mails_from_apple_mail(end_date=datetime.datetime(2025, 2, 23), days=7)
    ]

    # 2. Get Events from Mails
    mails = extract_events(
        mails=mails,
        batch_size=10
    )

    # TODO : 2-1. Add to DB
    

    # TODO : 3. Make priority based on user query
    

    # TODO : 4. Make & Send Personalized Email 


if __name__ == "__main__":
    main()
