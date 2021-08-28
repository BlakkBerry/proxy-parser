import argparse
from functools import reduce


class Mapper(argparse.Action):
    params = None

    def __call__(self, parser, args, values, option_string=None):
        proxy_types = set(values)

        parameter_string = reduce(lambda string, t: string + str(self.params[t]), proxy_types, '')

        setattr(args, self.dest, parameter_string)


class ProxyTypeMapper(Mapper):
    params = {
        'http': 'h',
        'https': 's',
        'socks4': '4',
        'socks5': '5'
    }


class AnonymityTypeMapper(Mapper):
    params = {
        'high': 4,
        'avg': 3,
        'low': 2
    }


def args_to_params(args: dict):
    params = '?'

    ports = args.pop('ports')

    if ports:
        params += f'ports={",".join(ports)}&'

    for key, value in args.items():
        if value:
            params += f'{key}={value}&'

    return params
