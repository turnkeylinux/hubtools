import simplejson as json
from pycurl_wrapper import Curl

class APIError(Exception):
    pass

class API:
    ALL_OK = 200
    CREATED = 201
    DELETED = 204

    @classmethod
    def request(cls, method, url, attrs={}, headers={}):
        # workaround: http://redmine.lighttpd.net/issues/1017
        if method == "PUT":
            headers['Expect'] = ''

        c = Curl(url, headers)
        func = getattr(c, method.lower())
        func(attrs)

        if not c.response_code in (cls.ALL_OK, cls.CREATED, cls.DELETED):
            name, description = c.response_data.split(":", 1)
            raise APIError(c.response_code, name, description)

        return json.loads(c.response_data)

class AttrDict(dict):
    def __getattr__(self, name):
        if name in self:
            return self[name]
        raise AttributeError("no such attribute '%s'" % name)

    def __setattr__(self, name, val):
        self[name] = val


