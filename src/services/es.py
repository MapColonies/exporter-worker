from elasticsearch import Elasticsearch, ConnectionError, RequestError
from src.config import read_config

__config = read_config()
esClient = Elasticsearch([{'host': __config['elasticsearch']['host_ip'], 'port': __config['elasticsearch']['port'],
                           'use_ssl': False}])


def update(doc):
    try:
        res = esClient.index(index=__config['elasticsearch']['index'], id=doc['taskId'], body=doc)
        print(res['result'])
    except ConnectionError as ce:
        raise Exception(
           f"Error connecting to database {ce.info}"
        )
    except RequestError as re:
        raise Exception(
            f"Request error from database ({re.error}): {re.info['error']['reason']}"
        )

