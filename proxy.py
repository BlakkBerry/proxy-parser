from enum import Enum


class Proxy:
    ip = None
    port = None
    type = None

    def __init__(self, ip, port, types):
        self.ip = ip
        self.port = port

        types_list = types.upper().split(',')

        try:
            if len(types_list) > 1:
                self.type = ProxyType[types_list[1].strip()]
            else:
                self.type = ProxyType[types_list[0].strip()]
        except KeyError:
            self.type = ProxyType.HTTP
            print('INVALID PROXY POLUCHAETSA') # todo remove!

    def __str__(self):
        return f'{self.ip}:{self.port}'


class ProxyType(Enum):
    HTTP = 'http'
    HTTPS = 'https'
    SOCKS4 = 'socks4'
    SOCKS5 = 'socks5'

    def __str__(self):
        return self.value
