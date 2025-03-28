import os
import json
import cv2
import numpy as np
import requests
from io import BytesIO
from PIL import Image
from rembg import remove
from typing import List
import numpy.typing as npt

DATA_INPUT_PATH = "data/products.json"
DATA_OUTPUT_PATH = "app/demo_data/demo_data.json"


class RandomProjectionHasher:
    def __init__(self, hash_size: int, input_dim: int, seed: int = 42):
        self.hash_size = hash_size
        self.input_dim = input_dim
        self.seed = seed
        self.planes = self._generate_uniform_planes()

    def _generate_uniform_planes(self):
        rs = np.random.RandomState(seed=self.seed)
        return rs.randn(self.hash_size, self.input_dim)

    def hash(self, input_point: npt.ArrayLike) -> str:
        input_point = np.array(input_point)
        projections = np.dot(input_point, self.planes.T)
        return "".join(["1" if i > 0 else "0" for i in projections])

    def hash_bulk(self, input_points: npt.ArrayLike) -> List[str]:
        projections_list = np.dot(input_points, self.planes.T)
        return [
            "".join(projections)
            for projections in (projections_list > 0).astype(int).astype(str)
        ]


hasher = RandomProjectionHasher(hash_size=32, input_dim=128)


def load_products():
    with open(DATA_INPUT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def download_image(url):
    try:
        response = requests.get(url, timeout=5)
        image = Image.open(BytesIO(response.content)).convert("RGB")
        return cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    except Exception as e:
        print(f"❌ 이미지 다운로드 실패: {url} - {e}")
        return None


def extract_sift_features(image):
    sift = cv2.SIFT_create()
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    keypoints, descriptors = sift.detectAndCompute(gray, None)
    return descriptors


def process_products(products):
    processed = []
    seen_urls = set()

    for product in products:
        url = product.get("image_url") or product.get("imageUrl")

        if url in seen_urls:
            continue
        seen_urls.add(url)

        # 특정 이미지 디버깅 로그
        if "JBy2PaqW.jpg" in url:
            print("🧩 현재 처리 중인 JBy2PaqW.jpg")

        image = download_image(url)
        if image is None:
            continue

        try:
            input_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            output_pil = remove(input_pil)
            image = cv2.cvtColor(np.array(output_pil), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"⚠️ 배경 제거 실패: {url} - {e}")
            continue

        descriptors = extract_sift_features(image)
        if descriptors is None:
            continue

        hashes = hasher.hash_bulk(descriptors)
        product["imageHashes"] = hashes
        processed.append(product)

    return processed



def save_demo_data(data):
    os.makedirs(os.path.dirname(DATA_OUTPUT_PATH), exist_ok=True)
    with open(DATA_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)



def main():
    print("📦 상품 불러오는 중...")
    products = load_products()

    print("🧠 특징점 추출 및 해시 생성 중...")
    processed = process_products(products)

    print(f"💾 해시 생성 완료된 상품 수: {len(processed)}")
    print("💾 데이터 저장 중...")
    save_demo_data(processed)
    print(f"✅ 완료! 저장 위치: {DATA_OUTPUT_PATH}")


if __name__ == "__main__":
    main()
