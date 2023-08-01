from abc import ABCMeta


__all__ = ('Singleton', 'ABCSingletonMixMeta', 'ABCSingletonMix')


class _SingletonMeta(type):

    def __new__(cls, name, base, dct):
        dct['__SINGLETON_INSTANCE__'] = None
        return super().__new__(cls, name, base, dct)

    def __call__(self, *args, **kwargs):

        instance = self.__dict__['__SINGLETON_INSTANCE__']
        if not instance:
            instance = super().__call__(*args, **kwargs)
            self.__SINGLETON_INSTANCE__ = instance

        instance = self.__dict__['__SINGLETON_INSTANCE__']
        assert isinstance(instance, self)
        return instance


class Singleton(metaclass=_SingletonMeta):
    ...


class ABCSingletonMixMeta(ABCMeta, _SingletonMeta):
    ...


class ABCSingletonMix(metaclass=ABCSingletonMixMeta):
    ...
