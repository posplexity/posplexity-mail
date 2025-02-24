import sqlite3
import os

# Apple Mail의 SQLite 데이터베이스 경로
MAIL_DB_PATH = os.path.expanduser('~/Library/Mail/V10/MailData/Envelope Index')

def fetch_mails_from_apple_mail():
    try:
        # SQLite DB 연결
        conn = sqlite3.connect(MAIL_DB_PATH)
        cursor = conn.cursor()

        # 2025년 1월 1일 이후로 받은 메일 중, 보낸 사람이 noreply@postech.ac.kr인 이메일만 가져오는 쿼리
        cursor.execute("""
            SELECT subject, sender, datetime(date_received, 'unixepoch') AS date_received
            FROM messages
            WHERE date_received >= strftime('%s', '2025-01-01')
            ORDER BY date_received;
        """)
        mails = cursor.fetchall()

        # 메일 개수 출력
        print(f"Total number of mails from noreply@postech.ac.kr since 2025-01-01: {len(mails)}")

        # 메일 정보 출력
        for mail in mails:
            subject, sender, date_received = mail
            print(f"Subject: {subject}")
            print(f"Sender: {sender}")
            print(f"Date Received: {date_received}")
            print("=" * 60)

        # 연결 종료
        conn.close()

    except sqlite3.Error as e:
        print(f"SQLite error: {e}")

# 실행
fetch_mails_from_apple_mail()