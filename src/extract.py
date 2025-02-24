from common.types.types import Mail, OfflineEvent, OnlineEvent
from src.llm_wrapper.gemini.inference import run_gemini
from src.utils.utils import async_wrapper


def extract_events(mails: list[dict], batch_size: int = 5) -> list[dict]:
    """
    메일 리스트를 배치 단위로 처리하여 이벤트를 추출합니다.
    """
    processed_mails = []
    
    # 배치 단위로 처리
    for i in range(0, len(mails), batch_size):
        batch = mails[i:i + batch_size]
        
        for mail in batch:
            async_task = [
                run_gemini(
                    target_prompt=
                )
            ]    
            
        processed_mails.extend(batch)
        
    return processed_mails
