from a10_utils.elastic_search_api import ElasticInterface
from datetime import datetime
import math

INDEX = 'a10_device_index'
DOC_TYPE = 'device'

INDEX_LOG = 'a10_device_log_index'
DOC_TYPE_LOG = 'log'

CUSTOMER_INDEX = "acxis_customer"
CUSTOMER_DOC_TYPE = "customer"

def get_customer_devices_by_platform(customer_id):
    """
    Gets ALL devices grouped by Platform for the given Customer ID
    :param customer_id:
    :return:
    """
    buckets = list()
    result_set = list()
    try:
        query_body = {
          "query": {
            "bool": {
              "must": {
                "match": {
                  "customer_id": customer_id
                }
              }
            }
          },
          "aggs": {
            "group_by_platform": {
              "terms": {
                "field": "platform"
              }
            }
          },
          "_source": {
                "includes": [
                    "*"
                ]
          },
          "size":200
        }

        result = ElasticInterface.search(index=INDEX, doc_type=DOC_TYPE, query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
            #print result_set
            buckets = result['aggregations']['group_by_platform']['buckets']
    except Exception, e:
        print e

    return buckets, result_set

def get_support_contracts_for_devices(serial_numbers_list):
    #print serial_numbers_list
    result_set = list()
    query_body = {
        "query": {
            "constant_score": {
                "filter": {
                    "terms": {
                        "serial_number":serial_numbers_list
                    }
                }
            }
        },
        "_source":{
            "includes":[
                "status", "end_date", "serial_number"
            ]
        }
    }
    result = ElasticInterface.search(index="acxis_support_contracts_06-20-2017", doc_type="contract", query_body=query_body)
    if result:
        result_dict  = ElasticInterface.process_search_results(result)
        result_set = result_dict['result_set']
    return result_set


def get_customer(customer_id):
    result_set = list()
    try:
        query_body = {
          "query": {
            "bool": {
              "must": {
                "match": {
                  "customer_id": customer_id
                }
              }
            }
          },
          "_source": {
                "includes": [
                    "*"
                ]
          }
        }

        result = ElasticInterface.search(index=CUSTOMER_INDEX, doc_type=CUSTOMER_DOC_TYPE, query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set


def get_aggregated_customers():
    all_customers_dict = dict()
    query_body = {
        "aggs": {
            "group_by_customer": {
                "terms": {
                    "field": "customer_id"
                }
            }
        },
        "_source": {
            "excludes": [
            "*"
            ]
        }
    }

    result = ElasticInterface.search(index=INDEX, doc_type=DOC_TYPE, query_body=query_body)
    if result:
        result_dict  = ElasticInterface.process_search_results(result)
        result_set = result_dict['result_set']
        #print result_set
        buckets = result['aggregations']['group_by_customer']['buckets']

        if buckets and len(buckets) > 0:
            must_list = list()
            for bucket in buckets:
                must_list.append(bucket['key'])

            query_body = {
                "query": {
                    "bool": {
                        "must": {
                            "terms": {
                                "customer_id": must_list
                            }
                        }
                    }
                },
                "_source": {
                    "includes": [
                      "customer_name", "customer_id"
                    ]
                }
            }

            result = ElasticInterface.search(index=CUSTOMER_INDEX, doc_type=CUSTOMER_DOC_TYPE, query_body=query_body)

            if result:
                list_of_hits = result['hits']['hits']
                for hit in list_of_hits:
                    all_customers_dict[hit['_source']['customer_id']] = hit['_source']['customer_name']

    return  all_customers_dict


def get_all_devices_by_platform():
    """
    Gets ALL devices grouped by Platform
    :return:
    """
    buckets = list()
    result_set = list()
    try:
        query_body = {
            "aggs": {
                "group_by_platform": {
                    "terms": {
                        "field": "platform",
                        "size": 100
                    }
                }
            },
            "_source": {
                "includes": [
                    "customer_name",
                    "serial_number",
                    "version",
                    "platform"
                ]
            },
            "size": 500
        }
        result = ElasticInterface.search(index=INDEX, doc_type=DOC_TYPE, query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
            #print result_set
            buckets = result['aggregations']['group_by_platform']['buckets']
    except Exception, e:
        pass

    return buckets, result_set


def get_all_cases():
    result_set = list()
    try:
        query_body = {
          "size":300
        }

        result = ElasticInterface.search(index="ACXIS_SUPPORT_READ", doc_type="case", query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set


def get_all_support_contracts():
    result_set = list()
    try:
        query_body = {
          "size":300
        }

        result = ElasticInterface.search(index="acxis_support_contracts_*", doc_type="contract", query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set

def get_glm_licenses(customer_id):
    result_set = list()
    query_body = {}
    try:
        if customer_id:
            # Query All Objects. This is for Customer view
            query_body = {
                "query": {
                    "term": {
                        "account_id": customer_id
                    }
                }
            }
        else:
            # Query All Objects. This is for Global view
            query_body = {
              "size":200
            }

        result = ElasticInterface.search(index="ACXIS_GLM_READ", doc_type="license", query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set


def get_all_defects():
    result_set = list()
    try:
        query_body = {
          "size":300
        }

        result = ElasticInterface.search(index="ACXIS_SUPPORT_BUGS_READ", doc_type="bug", query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set


def get_all_frs():
    result_set = list()
    try:
        query_body = {
            "query": {
                "bool": {
                    "should": [
                        {
                            "match": {
                                "fr.stage": "New"
                            }
                        },
                        {
                            "match": {
                                "fr.stage": "Analysis"
                            }
                        },
                        {
                            "match": {
                                "fr.stage": "Development"
                            }
                        },
                        {
                            "match": {
                                "fr.stage": "Feature Response"
                            }
                        }
                    ]
                }
        },
        "_source": {
            "includes": [
                "fr.id",
                "fr.title",
                "fr.stage",
                "fr.theater",
                "fr.customer",
                "fr.created",
                "fr.updated",
                "fr.product_tracks",
                "fr.release",
                "fr.submitted_by",
                "fr.product_manager",
                "fr.engineering_owner"
            ]
        },
        "size": 200,
        "sort": [
            {
                "fr.id": "desc"
            },
            "_score"
        ]
        }

        result = ElasticInterface.search(index="fr", doc_type="frdoc", query_body=query_body)
        if result:
            result_dict  = ElasticInterface.process_search_results(result)
            #print result_dict
            result_set = result_dict['result_set']
    except Exception, e:
        print e

    return result_set


def get_uptime_by_platform(customer_id=None):
    query_body = None
    platform_list = list()
    platform_version_list = list()
    if customer_id:
        query_body = {
            "query": {
                "term": {
                    "customer_id": customer_id
                }
            },
            "aggs": {
                "platform": {
                    "terms": {
                        "field": "platform",
                        "size":"80"
                    },
                    "aggs": {
                        "version": {
                            "terms": {
                                "field": "version"
                            },
                            "aggs": {
                                "up_time_days": {
                                    "terms": {
                                        "field": "up_time_days"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    else:
        query_body = {
            "aggs": {
                "platform": {
                    "terms": {
                        "field": "platform",
                        "size":"80"
                    },
                    "aggs": {
                        "version": {
                            "terms": {
                                "field": "version"
                            },
                            "aggs": {
                                "up_time_days": {
                                    "terms": {
                                        "field": "up_time_days"
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    result = ElasticInterface.search(index="ACXIS_DEVICE_UPTIME_READ", doc_type="device", query_body=query_body)
    if result:
        platform_buckets = result['aggregations']['platform']['buckets']
        if platform_buckets and len(platform_buckets) > 0:
            # Get platform list containing dicts of platform name and total devices
            platform_list = [ {"platform": x['key'], "total_devices": x['doc_count'] }for x in platform_buckets]
            #print platform_list

            # For platform get the version & device count for each version

            for platform in platform_buckets:
                platform_version_dict = dict()
                platform_version_buckets = platform['version']['buckets']
                version_list = list()
                for version in platform_version_buckets:
                    version_dict = dict()
                    version_key = version['key']

                    #version_dict['version'] = version['key']
                    version_dict['devices'] = version['doc_count']
                    ver_uptime_days_buckets = version['up_time_days']['buckets']

                    if ver_uptime_days_buckets:
                        version_device_detail = ', '.join(str(x['doc_count']) + '(' + str (x['key']) + ' days)'  for x in ver_uptime_days_buckets)
                        #print version_device_detail
                        version_dict['text'] = version_device_detail
                    else:
                        version_dict['text'] = ""

                    platform_version_dict[version_key] = version_dict
                    #version_list.append(version_dict)

                platform_version_dict['platform'] = platform['key']
                platform_version_dict['total_devices'] = platform['doc_count']
                #platform_version_dict['version_list'] = version_list
                platform_version_list.append(platform_version_dict)

            #print platform_version_list
        return platform_list, platform_version_list


def get_uptime_by_version(aggregation_by):
    query_body = {
        "aggs": {
            "version": {
                "terms": {
                    "field": aggregation_by[0],
                    "size": 15
                },
                "aggs": {
                    "uptime": {
                        "histogram": {
                            "field": "up_time_days",
                            "interval": 15,
                            "offset": 1
                        },
                        "aggs": {
                            "platform": {
                                "terms": {
                                    "field": aggregation_by[1]
                                }
                            }
                        }
                    }
                }
            }
        },
        "_source": {
            "excludes": [
                "*"
             ]
        }
    }

    result = ElasticInterface.search(index="ACXIS_DEVICE_UPTIME_READ", doc_type="device", query_body=query_body)
    if result:
        result_list = list()
        version_buckets = result['aggregations']['version']['buckets']

        if version_buckets and len(version_buckets) > 0:

            for version_bucket in version_buckets:
                version_dict = dict()
                version_key = version_bucket['key']
                uptime_buckets = version_bucket['uptime']['buckets']

                if uptime_buckets and len(uptime_buckets) > 0:

                    for index, uptime_bucket in enumerate(uptime_buckets):

                        uptime_dict = dict()

                        uptime_key = uptime_bucket['key']

                        uptime_dict["bucket"] = int(uptime_key)

                        platform_buckets = uptime_bucket['platform']['buckets']

                        if platform_buckets and len(platform_buckets) > 0:
                            version_device_detail = ''
                            if index == 0:
                                version_device_detail = 'From 0 days to ' + str(int(uptime_key)) + ' day(s) <br/>'
                            elif index < len(uptime_buckets) - 1:
                                prev_bucket = uptime_buckets[index - 1]
                                prev_uptime_key = prev_bucket['key']
                                version_device_detail = 'From ' + str(int(prev_uptime_key) + 1) + ' days to ' + str(int(uptime_key)) + ' day(s) <br/>'
                            elif index == len(uptime_buckets) - 1:
                                prev_bucket = uptime_buckets[index - 1]
                                prev_uptime_key = prev_bucket['key']
                                version_device_detail = 'More than ' + str(int(prev_uptime_key) + 1) + ' days <br/>'

                            version_device_detail += '<br/>'.join(x['key'] + '(' + str (x['doc_count']) + ' devices)'  for x in platform_buckets)

                            uptime_dict["text"] = version_device_detail

                        version_dict[str(int(uptime_key))] = uptime_dict

                version_dict['version'] = version_key

                result_list.append(version_dict)

        #print result_list
        return result_list


def get_support_cases_analytics_by_customer(search_index_or_alias, search_doc_type, aggregation_by, by_account= None):
    """
    This API works in 2 modes:
        - Get Analytics data for Support Cases by Customer.
        - Get Analytics data for Support Cases by Version/Component & vice-versa
    :return:
    """
    query_body = None

    """
    Mode 1:
    """
    if by_account:
        query_body = {
            "aggs": {
                "account": {
                    "terms": {
                        "field": "account",
                        "size": 15
                    },
                    "aggs": {
                        "variable_term": {
                            "terms": {
                                "field": aggregation_by,
                                "size": 15
                            }
                        }
                    }
                }
            },
            "_source": {
                "excludes": [
                "*"
                ]
            }
        }
    else:
        """
        Mode 2:
        """
        agg1 = None; agg2 = None

        if aggregation_by == 'reported_sub_release':
            agg1 = 'reported_sub_release'
            agg2 = 'component'
        elif aggregation_by == 'component':
            agg1 = 'component'
            agg2 = 'reported_sub_release'

        query_body = {
            "aggs": {
                "account": {
                    "terms": {
                        "field": agg1,
                        "size": 10
                    },
                    "aggs": {
                        "variable_term": {
                            "terms": {
                                "field": agg2,
                                "size": 15
                            }
                        }
                    }
                }
            },
            "_source": {
                "excludes": [
                "*"
                ]
            }
        }
    result = ElasticInterface.search(index= search_index_or_alias, doc_type=search_doc_type, query_body=query_body)
    if result:
        result_list = list()
        account_buckets = result['aggregations']['account']['buckets']

        if account_buckets and len(account_buckets) > 0:

            for account_bucket in account_buckets:
                version_dict = dict()
                account_key = account_bucket['key']
                #total_cases = account_bucket['doc_count']
                total_cases = 0

                variable_term_buckets = account_bucket['variable_term']['buckets']

                if variable_term_buckets and len(variable_term_buckets) > 0:
                    count = 0
                    for variable_term_bucket in variable_term_buckets:

                        cases_dict = dict()

                        variable_term_key = variable_term_bucket['key']

                        cases_dict["cases"] =  variable_term_bucket['doc_count']
                        total_cases += variable_term_bucket['doc_count']
                        version_dict[variable_term_key] = cases_dict

                version_dict['account'] =  (account_key[:16] + '..') if len(account_key) > 16 else account_key
                version_dict['total_cases'] = total_cases

                result_list.append(version_dict)

        #print result_list
        return result_list



def support_contract_analytics_by_name(timerange, customer_name=None):
    result_list = list()
    query_body = None
    current_month = datetime.now().month
    if timerange and timerange == 'next_month':
        query_body = {
            "query": {
                "bool": {
                    "must": {
                        "range": {
                            "end_date": {
                                "gte": str(current_month + 1) + "-01-2017",
                                "lte": str(current_month + 1) + "-30-2017",
                                "format": "MM-dd-yyyy"
                            }
                        }
                    }
                }
            },
            "aggs": {
                "licenses": {
                    "terms": {
                        "field": "contract_type",
                        "size": 30
                    }
                }
            }
        }
    elif timerange and timerange == 'next_quarter':
        current_quarter = int(math.ceil(float(current_month) / 3))
        range1 = None; range2= None
        next_quarter = current_quarter + 1
        if next_quarter ==1:
            range1 = "01-01-2018"
            range2 = "03-31-2018"
        elif next_quarter ==2:
            range1 = "04-01-2018"
            range2 = "06-30-2018"
        elif next_quarter ==3:
            range1 = "07-01-2017"
            range2 = "09-30-2017"
        elif next_quarter ==4:
            range1 = "10-01-2017"
            range2 = "12-31-2017"

        query_body = {
            "query": {
                "bool": {
                    "must": {
                        "range": {
                            "end_date": {
                                "gte": range1,
                                "lte": range2,
                                "format": "MM-dd-yyyy"
                            }
                        }
                    }
                }
            },
             "aggs": {
                "licenses": {
                    "terms": {
                        "field": "contract_type",
                        "size": 30
                    }
                }
            }
        }
    elif timerange and timerange == 'all':
        if customer_name:
            #For Customer View
            query_body = {
                "query": {
                    "bool": {
                        "should": {
                            "match": {
                                "account": {
                                    "query": customer_name,
                                    "operator": "and"
                                }
                            }
                        }
                    }
                },
                "aggs": {
                    "licenses": {
                        "terms": {
                            "field": "contract_type",
                            "size": 30
                        }
                    }
                },
                "_source": {
                    "excludes": [
                    "*"
                    ]
                }
            }
        else:
            #For Global View
            query_body = {
                "aggs": {
                    "licenses": {
                        "terms": {
                            "field": "contract_type",
                            "size": 30
                        }
                    }
                },
                "_source": {
                    "excludes": [
                    "*"
                    ]
                }
            }

    result = ElasticInterface.search(index= "acxis_support_contracts_*", doc_type="contract", query_body=query_body)
    if result:
        buckets = result['aggregations']['licenses']['buckets']
        if buckets and len(buckets) > 0:
            for bucket in buckets:
                if bucket['key'] == "":
                    bucket['key'] = "Others"
                    break

            result_list = buckets
    return result_list


def license_info_analytics(customer_id=None):
    result_list = list()
    query_body = None
    if customer_id:
        query_body = {
            "query":{
                "term":{
                    "account_id": customer_id
                }
            },
            "aggs": {
                "licenses": {
                    "terms": {
                        "field": "sku_type",
                        "size": 30
                    }
                }
            },
            "_source": {
                "excludes": [
                "*"
                ]
            }
        }
    else:
        query_body = {
            "aggs": {
                "licenses": {
                    "terms": {
                        "field": "sku_type",
                        "size": 30
                    }
                }
            },
            "_source": {
                "excludes": [
                "*"
                ]
            }
        }
    result = ElasticInterface.search(index= "ACXIS_GLM_READ", doc_type="license", query_body=query_body)
    if result:
        buckets = result['aggregations']['licenses']['buckets']
        if buckets and len(buckets) > 0:
            for bucket in buckets:
                if bucket['key'] == "":
                    bucket['key'] = "Others"
                    break

            result_list = buckets
    return result_list


def fr_analytics(search_index, search_doc_type, submitted_year, aggregation_by, customer_id=None):
    query_body = None
    if aggregation_by == 'status':
        if submitted_year == "ALL":
            if customer_id:
                # If ALL and Customer is present i.e. Customer View
                query_body = {
                    "query":{
                       "term":{
                           "fr.customer_id": customer_id
                       }
                    },
                    "aggs": {
                        "account": {
                            "terms": {
                                "field": "fr.stage",
                                "size": 10
                            },
                            "aggs": {
                                "variable_term": {
                                    "terms": {
                                        "field": "fr.product_tracks",
                                        "size": 15
                                    }
                                }
                            }
                        }
                    },
                    "_source": {
                        "excludes": [
                        "*"
                        ]
                    }
                }
            else:
                # If ALL and Customer is NOT present i.e. global view
                query_body = {
                    "aggs": {
                        "account": {
                            "terms": {
                                "field": "fr.stage",
                                "size": 10
                            },
                            "aggs": {
                                "variable_term": {
                                    "terms": {
                                        "field": "fr.product_tracks",
                                        "size": 15
                                    }
                                }
                            }
                        }
                    },
                    "_source": {
                        "excludes": [
                        "*"
                        ]
                    }
                }
        else:
            query_body = {
                "query": {
                    "bool": {
                          "must": {
                                "term": {
                                    "fr.created_year": submitted_year
                                }
                          }
                    }
                },
                "aggs": {
                    "account": {
                        "terms": {
                            "field": "fr.stage",
                            "size": 10
                        },
                        "aggs": {
                            "variable_term": {
                                "terms": {
                                    "field": "fr.product_tracks",
                                    "size": 15
                                }
                            }
                        }
                    }
                },
                "_source": {
                    "excludes": [
                    "*"
                    ]
                }
            }
    elif aggregation_by == 'owners':
        query_body = {
                "query": {
                    "bool": {
                        "must_not": [
                        {
                            "term": {
                                "fr.stage": "Closed"
                            }
                        },
                        {
                            "term": {
                                "fr.stage": "Duplicated"
                            }
                        }
                        ]
                    }
                },
                "aggs": {
                    "account": {
                        "terms": {
                            "field": "fr.engineering_owner",
                            "size": 12
                        },
                        "aggs": {
                            "variable_term": {
                                "terms": {
                                    "field": "fr.updated_year",
                                    "size": 3
                                }
                            }
                        }
                    }
                },
                "_source": {
                    "excludes": [
                    "*"
                    ]
                }
            }
    result = ElasticInterface.search(index= search_index, doc_type=search_doc_type, query_body=query_body)
    if result:
        result_list = list()
        account_buckets = result['aggregations']['account']['buckets']

        if account_buckets and len(account_buckets) > 0:

            for account_bucket in account_buckets:
                version_dict = dict()
                account_key = account_bucket['key']
                #total_cases = account_bucket['doc_count']
                total_cases = 0

                variable_term_buckets = account_bucket['variable_term']['buckets']

                if variable_term_buckets and len(variable_term_buckets) > 0:
                    count = 0
                    for variable_term_bucket in variable_term_buckets:

                        cases_dict = dict()

                        variable_term_key = variable_term_bucket['key']

                        cases_dict["cases"] =  variable_term_bucket['doc_count']
                        total_cases += variable_term_bucket['doc_count']
                        version_dict[variable_term_key] = cases_dict

                version_dict['account'] =  (account_key[:16] + '..') if len(account_key) > 16 else account_key
                version_dict['total_cases'] = total_cases

                result_list.append(version_dict)

        #print result_list
        return result_list


def fr_analytics_by_theater(search_index, search_doc_type, submitted_year):
    result_list = list()
    query_body = {
        "query": {
                "bool": {
                    "must": {
                        "term": {
                            "fr.created_year": submitted_year
                        }
                    }
                }
            },
            "aggs": {
                "theater": {
                    "terms": {
                        "field": "fr.theater",
                    "size": 10
                }
            }
        },
         "_source": {
                "excludes": [
                "*"
                ]
        }
    }
    result = ElasticInterface.search(index= search_index, doc_type=search_doc_type, query_body=query_body)
    if result:
        buckets = result['aggregations']['theater']['buckets']
        result_list = buckets

        #print result_list
    return result_list


def get_device_config_details(serial_number, customer_id, field_data):
    result_set = list()
    query_body = {
        "query":{
            "bool":{
                "must":[
                    {
                        "term":{
                            "customer_id": customer_id
                        }
                    },
                    {
                        "term":{
                            "serial_number": serial_number
                        }
                    }
                ]
            }
        },
        "_source":{
            "includes":[
                field_data
            ]
        }
    }
    result = ElasticInterface.search(index="acxis_device_config", doc_type="device", query_body=query_body)
    if result:
        result_dict  = ElasticInterface.process_search_results(result)
        result_set = result_dict['result_set']

    return result_set