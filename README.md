# 🖼️ 이미지 유사도 기반 검색 웹 서비스

## 📌 인덱싱 및 데모 동작 재현 방법

1. ### Elasticsearch 실행
   Docker 혹은 로컬에서 Elasticsearch 인스턴스를 실행합니다.
   ```bash
   docker-compose up -d  # 또는 직접 설치한 경우 elasticsearch 실행
   ```

2. ### FastAPI 서버 실행
   ```bash
   uvicorn app.main:app --reload
   ```

3. ### 프론트엔드 (index.html)
   `index.html` 파일을 브라우저로 열어 UI 접근
   > 또는 간단한 HTTP 서버 실행:
   ```bash
   python -m http.server
   ```

4. ### 인덱싱
   `demo_data.json` 데이터를 기반으로 다음 명령어 실행:
   ```bash
   python app/core/indexing.py
   ```

---

## 🔍 이미지 검색 동작 원리 (내가 이해한 방식)

1. 사용자가 이미지 URL을 입력
2. 서버는 이미지를 다운로드 → 배경 제거 → SIFT 특징점 추출
3. 특징점을 바탕으로 RandomProjection을 통해 32비트 이진 해시 생성
4. Elasticsearch에 인덱싱된 문서들의 해시와 **해밍 거리(Hamming Distance)**를 계산
5. 해밍 거리 5 이내의 유사 이미지가 있는 문서만 검색 결과로 반환
6. 결과는 React 기반 UI에 이미지, 상품명, 가격 정보로 표시됨

---

## 🧩 각 파트별 해결 과정

### ✅ 1. 크롤링
- `scrapy + selenium` 조합으로 `hsmoa.com`의 최근 30일 방송 상품 정보 수집
- 상품명, 가격, 이미지 URL, 쇼핑사 로고 URL 등 수집
- JSON 파일(`products.json`)로 저장

### ✅ 2. 이미지 전처리 및 해시 생성
- `rembg`로 배경 제거
- `cv2.SIFT_create()`를 통해 SIFT 특징점 추출
- `RandomProjectionHasher`로 32비트 해시값 생성

### ✅ 3. 인덱싱
- `app/core/indexing.py`에서 `demo_data.json` 기반으로 Elasticsearch 인덱싱 수행
- `productName`, `imageUrl`, `price`, `shoppingSite`, `imageHashes` 필드 포함

### ✅ 4. 유사 이미지 검색
- `/search?url=...` API 구현
- 클라이언트가 입력한 이미지의 해시와 Elasticsearch 문서들을 비교
- 해밍 거리 5 이내인 경우 `similar_docs`로 수집하여 응답

### ✅ 5. 프론트엔드
- React + Babel UMD 버전으로 구성된 단일 HTML 페이지
- 이미지 미리보기, 결과 목록, 가격순 정렬 기능 제공

---

## ⚠️ 어려웠던 부분 / Hurdle Point

- `rembg`와 OpenCV(SIFT) 사용 시 이미지 색상 왜곡 발생 → 전처리 파이프라인 조정 필요
- Elasticsearch에서 수천 개 해시값 중 해밍 거리 필터링 구현 시 성능 고려
- 일부 이미지에서 SIFT 특징점이 부족해 해시 생성 실패 → 예외 처리 로직 추가
- React Babel UMD 버전 사용 시 디버깅 불편함 → 콘솔 활용

---

## 🔗 참고 코드 및 레퍼런스

- OpenCV SIFT 문서: https://docs.opencv.org/4.x/da/df5/tutorial_py_sift_intro.html
- `rembg` 공식 문서: https://github.com/danielgatis/rembg
- Elasticsearch Python client: https://elasticsearch-py.readthedocs.io
- React UMD 환경: https://reactjs.org/docs/cdn-links.html

---

## 🤖 AI 어시스턴트 활용 내역

- Scrapy-Selenium 조합 XPath 최적화 조언 받음
- 이미지 전처리 파이프라인 설계 보조
- SIFT 해시 생성 코드 구현 도움
- Elasticsearch 유사도 검색 로직 점검
- React 기반 UI 흐름 설계 조언


> AI 어시스턴트: OpenAI ChatGPT (2025년 3월 기준 최신 모델 사용)

---

✅ **최종 결과:**  
이미지 URL을 기반으로 유사한 이미지와 가격, 상품명을 정확하게 조회하는 데모 구현 완료!
![Uploading image.png…]()
