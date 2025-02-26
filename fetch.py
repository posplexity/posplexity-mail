import os
import re
import plistlib
import quopri
from email import policy
from email.message import Message
from email.parser import BytesParser
from typing import Optional, Tuple

def parse_emlx(raw_data: bytes) -> Tuple[Message, Optional[dict]]:
    """
    Apple Mail .emlx 파일을 파싱한다.
    1) RFC5322(헤더 + 본문) 부분을 email.message.Message 객체로 만들고,
    2) 파일 끝에 붙은 plist (Apple Mail 메타데이터)가 있으면 dict로 반환한다.

    Args:
        raw_data (bytes): .emlx 파일의 전체 바이트 내용

    Returns:
        (parsed_email, plist_dict):
            parsed_email (Message): 파싱된 이메일 객체 (헤더, 본문, 첨부 등)
            plist_dict (dict | None): Apple Mail이 추가로 저장하는 plist 메타정보
    """
    # 1) plist 구문(<?xml ...) 시작점을 정규식으로 탐색
    match = re.search(b'<\\?xml.*', raw_data, flags=re.DOTALL)
    if match:
        xml_start_idx = match.start()
        # 메일 (RFC5322) 부분
        email_bytes = raw_data[:xml_start_idx].rstrip(b"\r\n")
        # plist 부분
        plist_bytes = raw_data[xml_start_idx:]
    else:
        # plist가 없거나 못 찾은 경우 → 전체를 메일로만 처리
        email_bytes = raw_data
        plist_bytes = None

    # 2) 이메일 부분 파싱
    #    policy=policy.default로 설정해주면 Python 3.6+ 기준으로
    #    새 헤더 파싱 규칙 및 디코딩이 적용된다.
    parsed_email: Message = BytesParser(policy=policy.default).parsebytes(email_bytes)

    # 3) plist 부분 파싱 (있으면 시도)
    plist_dict = None
    if plist_bytes:
        try:
            plist_dict = plistlib.loads(plist_bytes)
        except Exception:
            # plist 파싱 실패하면 None으로 둔다
            plist_dict = None

    return parsed_email, plist_dict

def extract_html_body(msg: Message) -> str:
    """
    주어진 email.message.Message 객체에서 text/html 파트를 찾아 디코딩하여 반환한다.
    - 멀티파트라면 각 파트를 순회하며 "text/html" 파트를 찾음
    - 싱글파트면 바로 본문 디코딩
    - 만약 text/html이 없으면 빈 문자열 반환

    Args:
        msg (Message): 이메일 메시지 객체

    Returns:
        html_content (str): 디코딩된 HTML 문자열 (없으면 "")
    """
    if msg.is_multipart():
        # 여러 파트가 있는 경우, 각 파트를 walk()하면서 text/html 파트를 찾는다.
        for part in msg.walk():
            if part.get_content_type() == "text/html":
                payload = part.get_payload(decode=True)
                # 인코딩 정보 가져오기
                charset = part.get_content_charset() or "utf-8"
                return payload.decode(charset, errors="replace")
        return ""  # text/html 파트를 못 찾은 경우
    else:
        # 싱글파트
        ctype = msg.get_content_type()
        if ctype == "text/html":
            payload = msg.get_payload(decode=True)
            charset = msg.get_content_charset() or "utf-8"
            return payload.decode(charset, errors="replace")
        else:
            return ""  # 싱글파트지만 text/plain만 있거나 다른 타입일 수 있음

def decode_quoted_printable(encoded_str: str, encoding: str = "utf-8") -> str:
    """
    Quoted-Printable 로 인코딩된 문자열을 직접 디코딩하는 헬퍼 함수.
    (이메일 모듈을 거치지 않고, 로 raw QP 문자열만 있을 때 사용)

    Args:
        encoded_str (str): =xx=yy 형태의 QP 인코딩된 문자열
        encoding (str): 최종 해석할 문자열 인코딩 (기본: 'utf-8')

    Returns:
        decoded (str): 사람이 읽을 수 있는 해석 결과
    """
    # str → bytes
    raw = encoded_str.encode(encoding, errors="replace")
    # quopri.decodestring로 QP 디코딩
    decoded_bytes = quopri.decodestring(raw)
    return decoded_bytes.decode(encoding, errors="replace")

# 실행 예시
if __name__ == "__main__":
    # emlx 파일 경로 (샘플)
    emlx_path = (
        "/Users/huhchaewon/Library/Mail/V10/"
        "BAF3E0C5-E996-4074-AEC0-A290F01EAD6C/"
        "교내회보.mbox/6C603F9C-7B10-487D-8AFD-C4286E4FC526/"
        "Data/6/Messages/6653.emlx"
    )

    # 1) emlx 파일 로드
    with open(emlx_path, "rb") as f:
        raw_data = f.read()
    
    # 2) parse_emlx() 호출
    email_msg, emlx_meta = parse_emlx(raw_data)
    breakpoint()
    # 3) 이메일 헤더 정보 출력
    print("=== [이메일 정보] ===")
    print("Subject:", email_msg["Subject"])
    print("From:", email_msg["From"])
    print("Date:", email_msg["Date"])

    # 4) HTML 본문 추출
    html_content = extract_html_body(email_msg)
    print("=== [HTML 본문] ===")
    print(html_content)

    # 5) plist 메타데이터 출력
    print("\n=== [Apple Mail plist 메타데이터] ===")
    print(emlx_meta)

    # 6) 예: Quoted-Printable 디코딩 테스트
    # 만약 직접 디코딩해야 할 QP 문자열이 있다면:
    qp_test = "=EC=98=81=ED=96=A5=EB=8F=84"
    print("\n=== [QP 디코딩 테스트] ===")
    print("원본:", qp_test)
    print("디코딩 결과:", decode_quoted_printable(qp_test))