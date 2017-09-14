
from elasticsearch import Elasticsearch, TransportError, ElasticsearchException, ConnectionError, ConnectionTimeout
from django.conf import settings

class ElasticInterface(object):
    """
    Generic Interface to communicate with ElasticSearch.
    All modules are required to use this interface to maintain code integrity.
    """
    # static variable to hold ES host connection dict objects. These does not hold actual connection object
    es_hosts = []

    @classmethod
    def _get_connection(cls):
        try:

                if len(ElasticInterface.es_hosts) == 0:
                    hosts = settings.ES_HOST
                    for h in hosts:
                        host_obj = {
                            'host': h,
                            'port': 9200,
                            'use_ssl': False
                        }
                        ElasticInterface.es_hosts.append(host_obj)

                es = Elasticsearch(
                    ElasticInterface.es_hosts,
                    sniff_on_start=True,
                    max_retries=100,
                    retry_on_timeout=True,
                    sniff_on_connection_fail=True,
                    sniff_timeout=1000
                )
                #print 'New ES Connection '
                es.cluster.health(wait_for_status='yellow', request_timeout=30)
                return es
        except ConnectionTimeout, cte:
            print 'Error Connecting to Elastic Search server instance. Now creating new connection !!', cte
            es = Elasticsearch([{'host': settings.ES_HOST, 'port': '9200', 'use_ssl': False}])
            es.cluster.health(wait_for_status='yellow', request_timeout=30)
            return es
        except ConnectionError, ce:
            print 'Error Connecting to Elastic Search server instance. Now creating new connection ! ', ce
            es = Elasticsearch([{'host': settings.ES_HOST, 'port': '9200', 'use_ssl': False}])
            es.cluster.health(wait_for_status='yellow', request_timeout=30)
            return es

    @classmethod
    def get_connection(cls):
        return cls._get_connection()

    @classmethod
    def index(cls, index, doc_type, body):
        # return ElasticInterface.es_instance.index(index=index, doc_type=doc_type, body=body)
        return cls._get_connection().index(index=index, doc_type=doc_type, body=body)

    @classmethod
    def update(cls, index, doc_type, post_id=None, body=None):
        # return ElasticInterface.es_instance.update(index=index, doc_type=doc_type,
        # id=post_id, body=body, request_timeout=30)
        return cls._get_connection().update(index=index, doc_type=doc_type, id=post_id, body=body, request_timeout=30)

    @classmethod
    def delete(cls, index, doc_type, post_id=None):
        # return ElasticInterface.es_instance.delete(index=index, doc_type=doc_type, id=post_id)
        return cls._get_connection().delete(index=index, doc_type=doc_type, id=post_id)

    @classmethod
    def search(cls, index, doc_type, query_body):
        # return ElasticInterface.es_instance.search(index=index, doc_type=doc_type,
        # body=query_body, request_timeout=30)
        return cls._get_connection().search(index=index, doc_type=doc_type, body=query_body, request_timeout=30)

    @classmethod
    def get(cls, index, doc_type, post_id, _source=False, refresh=False):
        # return ElasticInterface.es_instance.get(index=index, doc_type=doc_type, id=post_id, _
        # source=_source, refresh=refresh, request_timeout=30)
        return cls._get_connection().get(index=index, doc_type=doc_type, id=post_id,
                                         _source=_source, refresh=refresh, request_timeout=30)

    @classmethod
    def process_search_results(cls, results):
        """
        Generic API to process search results. API will return a result_set.
        API's should write local code to fulfil custom requirement.
        :param results:
        :return:
        """
        result_set = []
        if results:
            hits = results['hits']
            took = results['took']

            if hits:
                total_results = hits['total']

                dict_list = hits['hits']
                # print 'hits2 == ', dict_list
                if dict_list and len(dict_list) > 0:
                    for d in dict_list:
                        _source = d['_source']
                        _source['post_id'] = d['_id']
                        # print _source
                        result_set.append(_source)

        return {'took': took, 'total': total_results, 'result_set': result_set}

    @classmethod
    def check_index_alive_status(cls, index):
        """
        Global Function to check whether the index exists
        :param index:
        :return: Boolean value whether index exists or not
        """
        conn = cls._get_connection()
        return conn.indices.exists(index)
