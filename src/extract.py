from common.types.types import Events
from src.llm_wrapper.gemini.inference import run_gemini
from src.utils.utils import async_wrapper

import asyncio

def extract_events(mails: list[dict], batch_size: int = 5) -> list[dict]:
    """
    메일 리스트를 배치 단위로 처리하여 이벤트를 추출합니다.
    """
    processed_mails = []
    
    # 배치 단위로 처리
    for i in range(0, len(mails), batch_size):
        batch, async_task = mails[i:i + batch_size], []
        # TODO : parse해서 보도록 코드 수정, url -> zoom 아니면 없게 prompt 수정, 없으면 왜 없는지 이유 뱉기
        for mail in batch:
            async_task.append(
                run_gemini(
                    target_prompt=str(mail.__dict__),
                    prompt_in_path="extract.json",
                    output_structure=Events,
                    model="gemini-2.0-flash"
                )
            )
        main_events = asyncio.run(async_wrapper(async_task))
        for idx, event in enumerate(main_events):
            print(f"MAIL {idx}")
            print(f"offline_events: {event[0].offline_events}")
            print(f"online_events: {event[0].online_events}\n")

        breakpoint()
        processed_mails.extend(batch)
        
    return processed_mails
