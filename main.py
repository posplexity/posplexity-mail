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
    mails = extract_events(mails)


    batch_size = 5  # 한 번에 처리할 메일 수
    for i in range(0, len(mails), batch_size):
        batch_mails = mails[i:i + batch_size]
        for mail in batch_mails:



if __name__ == "__main__":
    main()
