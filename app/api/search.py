from fastapi import APIRouter
from fastapi.responses import JSONResponse

from app.core.hashing import get_image_hashes
from app.core.es_client import es
from app.core.utils import download_image_and_preprocess
from app.core.hash_utils import hamming_distance  # 새로 생성할 파일에서 import

router = APIRouter()

@router.get("/search")
def search_similar_images(url: str):
    try:
        print("👉 URL:", url)
        image = download_image_and_preprocess(url)
        print("✅ 이미지 전처리 완료")

        if image is None:
            return {"error": "이미지 처리 실패"}

        query_hashes = get_image_hashes(image)
        print("✅ 해시 생성 완료", query_hashes)

        # Elasticsearch에서 최대 1000개 문서 가져오기
        all_docs = es.search(index="products", body={
            "size": 1000,
            "_source": ["productName", "imageUrl", "price", "imageHashes", "shoppingSite"]
        })

        # 해밍 거리 기반 필터링
        threshold = 5  # 허용 해밍 거리
        similar_docs = []

        for hit in all_docs["hits"]["hits"]:
            doc = hit["_source"]
            for h1 in query_hashes:
                for h2 in doc.get("imageHashes", []):
                    if hamming_distance(h1, h2) <= threshold:
                        similar_docs.append(doc)
                        break
                else:
                    continue
                break

        print(f"✅ 유사 이미지 검색 완료: {len(similar_docs)}개")
        return similar_docs

    except Exception as e:
        print("❌ 에러 발생:", str(e))
        return {"error": str(e)}
