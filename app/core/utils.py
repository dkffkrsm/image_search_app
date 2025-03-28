import requests
import numpy as np
import cv2
from PIL import Image
from io import BytesIO
from rembg import remove


def download_image_and_preprocess(url: str):
    # 1. 이미지 다운로드
    response = requests.get(url, timeout=5)
    image = Image.open(BytesIO(response.content)).convert("RGB")

    # 2. 배경 제거
    image_no_bg = remove(image)

    # 3. OpenCV로 변환 후 다시 PIL로 변환 (SIFT가 OpenCV로 적용되어 있을 경우)
    image_no_bg_np = cv2.cvtColor(np.array(image_no_bg), cv2.COLOR_RGB2BGR)

    # 🔄 PIL 객체로 변환해서 리턴 (get_image_hashes가 기대하는 형식)
    return Image.fromarray(cv2.cvtColor(image_no_bg_np, cv2.COLOR_BGR2RGB))



