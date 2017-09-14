import time
import requests
import logging

log = logging.getLogger(__name__)

APP_REGISTRY = dict()
APP_REGISTRY["Asset Info"] = [[8004], "/asset_info"]
#APP_REGISTRY["Support Cases"] = [[8005], "/support_cases"]
#APP_REGISTRY["Forums"] = [[8006], "/forums"]

class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]

class Acxis_apps(object):
    __metaclass__ = Singleton

    app_list = list()
    started = False

    def __init__(self):
        #self.start_up()
        pass

    def load_global_apps(self):
        return Acxis_apps.app_list

    def load_customer_apps(self):
        return Acxis_apps.app_list


    # def get_apps(self):
    #     if self.view_type == 'global':
    #         return self._load_global_apps()
    #     elif self.view_type == 'customer':
    #         return self._load_customer_apps()

    def health_check(self):
        print 'health_check called'
        log.debug('health_check called')
        #print APP_REGISTRY
        #while True:
        print("This prints once 20 seconds.")
        log.debug("This prints once 20 seconds.")
        time.sleep(20)
        apps_list = list()
        for key, value in APP_REGISTRY.items():
            print key
            print value
            ports_list = value[0]
            app_uri = value[1]

            try:
                app_url = 'http://127.0.0.1:' + str(ports_list[0]) + app_uri + '/health/'
                #print app_url
                app_response = requests.get(app_url, timeout=4)
                #print app_response.status_code
                if app_response.status_code == 200:
                    app = (key, "UP", value[1] )

            except Exception, e:
                app = (key, "DOWN", value[1] )
                pass
            finally:
                apps_list.append(app)

        Acxis_apps.app_list = apps_list

    def start_up(self):
        self.started = True
        print 'startt up called'
        log.debug('startup called !!!!')
        while True:
            self.health_check()
        print 'startt up complete'
        log.debug('startup complete !!!!')
        #t.join(timeout=None)


