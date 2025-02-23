import logging
from PIL import Image
from io import BytesIO
from openai import APIConnectionError

from src.utils.decorator import retry_async

import requests, os, json, time
from google import genai

prompt_base_path = "src/llm_wrapper/prompt"
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))


def encode_image(image_source):
    """
    이미지 경로가 URL이든 로컬 파일이든 Pillow Image 객체이든 동일하게 처리하는 함수.
    이미지를 열어 google.genai.types.Part 객체로 변환합니다.
    Pillow에서 지원되지 않는 포맷에 대해서는 예외를 발생시킵니다.
    """
    try:
        # 이미 Pillow 이미지 객체인 경우 그대로 사용
        if isinstance(image_source, Image.Image):
            image = image_source
        else:
            # URL에서 이미지 다운로드
            if isinstance(image_source, str) and (
                image_source.startswith("http://")
                or image_source.startswith("https://")
            ):
                response = requests.get(image_source)
                image = Image.open(BytesIO(response.content))
            # 로컬 파일에서 이미지 열기
            else:
                image = Image.open(image_source)

        # 이미지 포맷이 None인 경우 (메모리에서 생성된 이미지 등)
        if image.format is None:
            image_format = "JPEG"
        else:
            image_format = image.format

        # 이미지 포맷이 지원되지 않는 경우 예외 발생
        if image_format not in Image.registered_extensions().values():
            raise ValueError(f"Unsupported image format: {image_format}.")

        buffered = BytesIO()
        # PIL에서 지원되지 않는 포맷이나 다양한 채널을 RGB로 변환 후 저장
        if image.mode in ("RGBA", "P", "CMYK"):  # RGBA, 팔레트, CMYK 등은 RGB로 변환
            image = image.convert("RGB")
        image.save(buffered, format="JPEG")
        
        return genai.types.Part.from_bytes(data=buffered.getvalue(), mime_type="image/jpeg")

    except requests.exceptions.RequestException as e:
        raise ValueError(f"Failed to download the image from URL: {e}")
    except IOError as e:
        raise ValueError(f"Failed to process the image file: {e}")
    except ValueError as e:
        raise ValueError(e)


@retry_async(
    max_attempts=3, delay_seconds=2, exceptions=(ConnectionError, APIConnectionError)
)
async def run_gemini(
    target_prompt: str,
    prompt_in_path: str,
    output_structure,
    img_in_data: str = None,
    model: str = "gemini-2.0-flash",
) -> str:
    with open(
        os.path.join(prompt_base_path, prompt_in_path), "r", encoding="utf-8"
    ) as file:
        prompt_dict = json.load(file)

    system_prompt = prompt_dict["system_prompt"]
    user_prompt_head, user_prompt_tail = (
        prompt_dict["user_prompt"]["head"],
        prompt_dict["user_prompt"]["tail"],
    )

    user_prompt_text = "\n".join([user_prompt_head, target_prompt, user_prompt_tail])

    input_content = [user_prompt_text]

    if img_in_data is not None:
        encoded_image = encode_image(img_in_data)
        input_content.append(encoded_image)
        
    # logger - INFO
    logging.info("Requested API for chat completion response...")
    start_time = time.time()
    chat_completion = await client.aio.models.generate_content(
        model=model,
        contents=input_content,
        config={
            "system_instruction": system_prompt,
            "response_mime_type": "application/json",
            "response_schema": output_structure
        }
    )
    chat_output = chat_completion.parsed

    input_token = chat_completion.usage_metadata.prompt_token_count 
    output_token = chat_completion.usage_metadata.candidates_token_count
    pricing = input_token / 1000000 * 0.1 * 1500 + output_token / 1000000 * 0.7 * 1500

    logging.info(
        f"[GEMINI] Request completed. Time taken: {time.time()-start_time:.2f} / Pricing(KRW) : {pricing:.2f}"
    )
    return chat_output, chat_completion