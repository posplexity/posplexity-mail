import sqlite3, os, logging, datetime
from common.config.config import MAIL_DIRECTORY

def fetch_mails_from_apple_mail(end_date:datetime.datetime=None, days:int=7):
    try:
        # end_date가 None이면 현재 시간을 사용
        if end_date is None:
            end_date = datetime.datetime.now()
        # days를 이용해 시작 날짜 계산
        start_date = end_date - datetime.timedelta(days=days)
        
        # SQLite DB 연결
        db_path = os.path.expanduser(MAIL_DIRECTORY)
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Apple Mail에서 교내회보 필터링
        cursor.execute("""
            SELECT 
                s.subject,
                sm.summary,
                a.address,
                datetime(m.date_received, 'unixepoch') AS date_received
            FROM messages m
            JOIN addresses a ON m.sender = a.rowid 
            JOIN subjects s ON m.subject = s.ROWID
            JOIN summaries sm ON m.summary = sm.ROWID
            WHERE a.address = 'noreply@postech.ac.kr'
              AND m.date_received >= strftime('%s', ?)
              AND m.date_received <= strftime('%s', ?)
            ORDER BY m.date_received;
        """, (start_date.strftime('%Y-%m-%d %H:%M:%S'), 
              end_date.strftime('%Y-%m-%d %H:%M:%S')))
        
        mails = cursor.fetchall()
        logging.info(f"📩 Total number of mails from noreply@postech.ac.kr between {start_date} and {end_date}: {len(mails)}")

        conn.close()
        return mails

    except sqlite3.Error as e:
        logging.error(f"SQLite error: {e}")
        raise e
