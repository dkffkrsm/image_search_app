import os
import json
import scrapy
from datetime import datetime, timedelta
from urllib.parse import urlparse
from scrapy.selector import Selector

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


class ProductsSeleniumSpider(scrapy.Spider):
    name = 'products_selenium'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def closed(self, reason):
        self.driver.quit()

    def clean_url(self, url):
        """Query string 제거해서 고유 이미지 URL 생성"""
        return urlparse(url)._replace(query="").geturl()

    def start_requests(self):
        base_url = "https://hsmoa.com/?date={}"
        today = datetime.today()
        date_list = [(today - timedelta(days=i)).strftime('%Y%m%d') for i in range(30)]

        all_products = []
        seen_keys = set()

        for date in date_list:
            url = base_url.format(date)
            self.logger.info(f"크롤링 중: {url}")
            self.driver.get(url)

            try:
                # 렌더링 완료될 때까지 대기
                WebDriverWait(self.driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cursor-pointer.rounded-\\[2px\\]"))
                )
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                WebDriverWait(self.driver, 5).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, "div.cursor-pointer.rounded-\\[2px\\]"))
                )
            except Exception as e:
                self.logger.warning(f"페이지 로딩 실패: {e}")
                continue

            html = self.driver.page_source
            selector = Selector(text=html)

            # 디버깅용 HTML 저장
            file_path = f"splash_output_{date}.html"
            with open(file_path, "w", encoding="utf-8") as f:
                f.write(html)

            product_elements = self.driver.find_elements(By.CSS_SELECTOR, "div.cursor-pointer.rounded-\\[2px\\]")

            for el in product_elements:
                try:
                    title = price = shop_logo = image_url = None

                    # 상품명
                    try:
                        title = el.find_element(By.CSS_SELECTOR, "p.tracking-tight").text.strip()
                    except:
                        pass

                    # 가격
                    try:
                        price_el = el.find_element(By.CSS_SELECTOR, "span.font-bold")
                        price = price_el.text.strip()
                    except:
                        pass

                    # 쇼핑사 로고
                    try:
                        logo_el = el.find_element(By.CSS_SELECTOR, "img[src*='cdn.static.hsmoa.com/logo']")
                        shop_logo = logo_el.get_attribute("src")
                    except:
                        pass

                    # 상품 이미지
                    try:
                        img_el = el.find_element(By.CSS_SELECTOR, "img[src*='buzzni.com'], img[src*='cdn.image.buzzni.com'], img[src*='image.hmall.com']")
                        image_url = self.clean_url(img_el.get_attribute("src"))
                    except:
                        pass

                    # 필수 정보가 모두 존재할 때만 저장
                    if not title or not image_url or not shop_logo:
                        continue

                    unique_key = f"{title}_{shop_logo}_{date}"
                    if unique_key not in seen_keys:
                        seen_keys.add(unique_key)
                        all_products.append({
                            "product_name": title,
                            "price": price if price else None,
                            "shop_logo_url": shop_logo,
                            "image_url": image_url,
                            "date": date
                        })

                except Exception as e:
                    self.logger.warning(f"상품 정보 파싱 중 오류 발생: {e}")

        self.save_to_json(all_products)
        self.logger.info(f"✅ 총 {len(all_products)}개의 상품 저장 완료")

        # Scrapy 워크플로우를 위해 Dummy 요청
        yield scrapy.Request(url="https://example.com", callback=self.do_nothing)

    def do_nothing(self, response):
        self.logger.info("Selenium 크롤링 완료 (Scrapy dummy request)")

    def save_to_json(self, products):
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../"))
        data_path = os.path.join(project_root, "data", "products.json")
        os.makedirs(os.path.dirname(data_path), exist_ok=True)

        try:
            with open(data_path, "r", encoding="utf-8") as f:
                existing_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            existing_data = []

        existing_keys = {f"{item['product_name']}_{item['shop_logo_url']}_{item['date']}" for item in existing_data}
        new_products = [
            item for item in products
            if f"{item['product_name']}_{item['shop_logo_url']}_{item['date']}" not in existing_keys
        ]

        existing_data.extend(new_products)

        with open(data_path, "w", encoding="utf-8") as f:
            json.dump(existing_data, f, ensure_ascii=False, indent=4)
