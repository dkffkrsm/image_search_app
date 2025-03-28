from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from app.api.search import router as search_router
import app.core.indexing as indexing
from fastapi.responses import FileResponse

app = FastAPI()

# 🔹 이미지 검색 API 라우터 등록
app.include_router(search_router)

# 🔹 정적 파일 및 템플릿 설정
app.mount("/static", StaticFiles(directory="app/static"), name="static")
templates = Jinja2Templates(directory="app/templates")

# 🔹 루트 경로에서 index.html 렌더링
@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return FileResponse("app/templates/index.html")

# 🔹 앱 시작 시 Elasticsearch에 demo_data 인덱싱
@app.on_event("startup")
def startup_event():
    indexing.index_demo_data()
