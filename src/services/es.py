from elasticsearch import Elasticsearch
es = Elasticsearch([{'host': '10.28.11.49', 'port': 9200, 'url_prefix': 'es', 'use_ssl': False}])

def update(doc):
    res = es.index(index='test-index', doc_type=doc['taskId'], body=doc)
    print(res['result'])
