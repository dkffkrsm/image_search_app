import os
import json
from elasticsearch import Elasticsearch, helpers

ES_HOST = os.getenv("ES_HOST", "http://localhost:9200")
INDEX_NAME = "products"
DEMO_DATA_PATH = "app/demo_data/demo_data.json"

def load_demo_data():
    with open(DEMO_DATA_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def create_index_if_not_exists(es):
    if not es.indices.exists(index=INDEX_NAME):
        es.indices.create(index=INDEX_NAME)

def generate_bulk_data(products):
    for product in products:
        yield {
            "_index": INDEX_NAME,
            "_source": product
        }

# 🔹 FastAPI에서도 호출 가능하게 export 해줄 함수
def index_demo_data():
    print("🚀 Elasticsearch에 연결 중...")
    es = Elasticsearch(ES_HOST)
    
    print(f"📁 {INDEX_NAME} 인덱스 생성 여부 확인 중...")
    create_index_if_not_exists(es)

    print("📦 demo_data 로딩 중...")
    products = load_demo_data()

    print(f"📤 {len(products)}개 문서를 Elasticsearch에 인덱싱 중...")
    helpers.bulk(es, generate_bulk_data(products))
    print("✅ 인덱싱 완료!")

# 🔹 터미널에서 직접 실행할 경우
if __name__ == "__main__":
    index_demo_data()
