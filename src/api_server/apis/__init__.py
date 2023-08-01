from abc import ABCMeta, abstractmethod, abstractproperty
from typing import List, Type


class APIBaseMeta(type):

    def __new__(cls, name, base, dct):
        new_cls = super().__new__(cls, name, base, dct)

        if name != 'APIBase':
            APIBase.REGISTERED_APIS.append(new_cls)

        return new_cls


class ABCAPIBaseMix(ABCMeta, APIBaseMeta):
    ...


class APIBase(metaclass=ABCAPIBaseMix):

    REGISTERED_APIS: List[Type] = []

    class APIRouterEntry(object):

        def __init__(self, action, cb):
            self.action = action
            self.cb = cb

    def __init__(self):
        self._api_route_entries = []
        self.define_actions_mapping()

    def add_entry(self, action, cb):
        self._api_route_entries.append(self.APIRouterEntry(action, cb))

    @abstractproperty
    def controller(self):
        ...

    @abstractproperty
    def url(self) -> str:
        ...

    @abstractmethod
    def define_actions_mapping(self):
        ...

    @property
    def route_entries(self):
        return {e.action: e.cb for e in self._api_route_entries}
