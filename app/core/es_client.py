from elasticsearch import Elasticsearch

# docker-compose 환경에서는 "http://es:9200", 로컬 개발 시 "http://localhost:9200"
es = Elasticsearch("http://es:9200")
