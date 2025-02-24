import os
import email

# TODO : Parsing 함수 제작, 교내 회보 메일 자동 파싱 코드 작성 
with open('', 'rb') as f:
    raw_data = f.read()
# raw_data를 email.parser.BytesParser 등으로 파싱
msg = email.message_from_bytes(raw_data)
breakpoint()