from azure.identity import DeviceCodeCredential
import requests

CLIENT_ID = "앱등록시 받은 CLIENT_ID"
TENANT_ID = "학교 테넌트 ID (도메인별로)"

# 1) 기기 코드 흐름으로 로그인 & 토큰 받기
credential = DeviceCodeCredential(
    client_id=CLIENT_ID,
    tenant_id=TENANT_ID
)
token = credential.get_token("https://graph.microsoft.com/.default")

# 2) Graph API 호출
url = "https://graph.microsoft.com/v1.0/me/messages"
headers = {
    "Authorization": f"Bearer {token.token}",
    "Content-Type": "application/json"
}
resp = requests.get(url, headers=headers)
print(resp.json())

