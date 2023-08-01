from .apis import APIBase
from importlib import import_module
from os import listdir
from os.path import dirname, join


caller_module = import_module('__main__')
package_name = caller_module.__package__
directory = join(dirname(__file__), 'apis')
file: str
for file in listdir(directory):
    if file.startswith('__init__.py'):
        continue

    if file.split('.')[-1] in ('py', 'pyc'):
        module_name = file[:file.rfind('.')]  # Remove the '.py/pyc' extension
        module = import_module(f'{package_name}.apis.{module_name}')


class Routes(object):

    def __iter__(self):

        for api_cls in APIBase.REGISTERED_APIS:
            api_obj = api_cls()
            yield api_obj.url, api_obj.route_entries

    items = __iter__


API_ROUTES = Routes()


__all__ = ['API_ROUTES']
