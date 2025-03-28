import scrapy


class ScheduleSpider(scrapy.Spider):
    name = "schedule"
    allowed_domains = ["hsmoa.com"]
    start_urls = ["https://hsmoa.com"]

    def parse(self, response):
        pass
