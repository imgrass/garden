from .exception import ExceptionBase, ExceptionInfo, register_exception
from abc import ABCMeta, abstractclassmethod, abstractproperty
from typing import Tuple


class DescriptorSyntaxError(ExceptionBase):
    '''
    This error can only be thrown when building the descriptor. This is a pure
    syntax error and is not acceptable.
    '''

    @register_exception
    def invalid_init_args(info: ExceptionInfo, args):
        info.tell_me('Descriptor expect 1 or 2 types, but recieved '
                     f'{len(args)}: ({args})')

    @register_exception
    def unsupport_compound_type(info: ExceptionInfo, compound_type,
                                supported_compound_types):
        info.tell_me(f'Compund type ({compound_type}) is not in the supported '
                     f'compound types {supported_compound_types}')

    @register_exception
    def invalid_element_type(info: ExceptionInfo, element_type):
        info.tell_me('Element type should be a class, but type(element_type) '
                     f'is "{type(element_type)}", not <class type>')

    @register_exception
    def invalid_default_value(info: ExceptionInfo, default, element_type,
                              error):
        info.tell_me(f'The default value ({default}) used to initialize the '
                     'descriptor does not match the specified element type '
                     f'({element_type}), the details are as follows: {error}')


class DescriptorRuntimeError(ExceptionBase):
    '''
    This error occurs when assigning value to variables which use the
    descriptor protocol, which is possible.
    '''

    @register_exception
    def invalid_value(info: ExceptionInfo, value, element_type, error):
        info.tell_me(f'The value ({value}) assigned to the variable dose not '
                     f'match the element type ({element_type}), the details '
                     f'are as follows: {error}')


class Descriptor(object):
    r'''
    This class an implementation of Descriptor protocol in Python.
    It provides the following functions:

      - Describe the type of variables, which could aslo be described even if
        it is a composite type, like <list> or <dict>.
      - Is this variable a required value.
      - Default value

    The usage of it is shown as below:

    >>> class Demo:
    >>>     count = Descriptor(int, default=0)
    >>>     color = Descriptor(EnumColor, required=False)
    >>>     friends = Descriptor(list, Friend, default=[])
    >>>
    >>> demo = Demo()
    >>> demo.count = 1

    This descriptor protocol will add a '__descriptor__' variable to the
    __dict__ of the instance, the type is a dictionary, each variable is used
    as the key of the dictionary, and their values are used as the value of
    the dictionary.
    For example, in the above example, these variables will be stored here:

    >>> demo.__dict__['__descriptor__']
    >>> {'count': 1, }
    '''

    _name = None
    _compound_type = None
    _element_type = None
    _default = None
    _required = True
    _own_class_name = None

    _supported_compound_types = (dict, list)

    def __init__(self, *args, default=None, required=True):

        arg_count = len(args)
        if arg_count > 2 or arg_count == 0:
            raise DescriptorSyntaxError.invalid_init_args(args)

        self._element_type = args[-1]
        if arg_count == 1:
            self._compound_type = None
        else:
            self._compound_type = args[0]

        if self._compound_type and \
                self._compound_type not in self._supported_compound_types:
            raise DescriptorSyntaxError.unsupport_compound_type(
                self._compound_type, self._supported_compound_types)

        if not isinstance(self._element_type, type):
            raise DescriptorSyntaxError.invalid_element_type(
                self._element_type)

        is_valid, error = self._validate_value(default)
        if not is_valid:
            raise DescriptorSyntaxError.invalid_default_value(
                default, self._element_type, error)

        self._default = default
        self._required = bool(required)

    def __repr__(self):
        if self._compound_type:
            _type = '%s[%s]' % (self._compound_type.__name__,
                                self._element_type.__name__)
        else:
            _type = self._element_type.__name__

        return f'Descriptor {self._name}, type is {_type}. required: ' \
               f'{self._required}, default: {self._default}'

    @property
    def name(self):
        return self._name

    @property
    def compound_type(self):
        return self._compound_type

    @property
    def element_type(self):
        return self._element_type

    @property
    def default(self):
        return self._default

    @property
    def required(self):
        return self._required

    def generate_default_value(self):
        if self.compound_type:
            return self.compound_type()

        return self.element_type()

    def __set_name__(self, own, name):
        self._name = name
        self._own_class_name = own.__name__

    def __get__(self, obj, type=None):
        try:
            return obj.__dict__['__descriptors__'][self._name]
        except KeyError:
            return self._default

    def __set__(self, obj, value):

        dct = obj.__dict__.setdefault('__descriptors__', {})
        is_valid, error = self._validate_value(value)
        if not is_valid:
            raise DescriptorRuntimeError.invalid_value(
                value, self._element_type, error)
        dct[self._name] = value

    def _validate_value(self, value) -> Tuple[bool, str]:

        if self._compound_type is list:
            if not isinstance(value, self._compound_type):
                return False, (
                    f'The descriptor property of ({self._name}) owned by '
                    f'<class {self._own_class_name}> is a compound type '
                    f'<list>, not {type(value)}')
            for element in value:
                if not isinstance(element, self._element_type):
                    return False, (
                        f'The descriptor property of ({self._name}) owned by '
                        f'<class {self._own_class_name}> is a list of element '
                        f'whose type is {self._element_type}, but found a '
                        f'element ({element}) with type {type(element)}')
        elif self._compound_type is dict:
            if not isinstance(value, self._compound_type):
                return False, (
                    f'The descriptor property of ({self._name}) owned by '
                    f'<class {self._own_class_name}> is a compound type '
                    f'<dict>, not {type(value)}')
            for key, element in value.items():
                if not isinstance(element, self._element_type):
                    return False, (
                        f'The descriptor property of ({self._name}) owned by '
                        f'<class {self._own_class_name}> is a dict of element '
                        f'whose value type is {self._element_type}, but found '
                        f'a k-v pair ({key}:{element}) with type '
                        f'{type(element)}')
        else:
            if not isinstance(value, self._element_type):
                return False, (
                    f'The descriptor property of ({self._name}) owned by '
                    f'<class {self._own_class_name}> is an object whose type '
                    f'is {self._element_type}, but a value ({value}) with '
                    f'type {type(value)} was given')

        return True, ''


class _MetaBase(type):

    def __new__(cls, name, bases, dct):
        if name == '_Base':
            return super().__new__(cls, name, bases, dct)

        fields = dct.pop('__fields__', None)
        if fields is None:
            raise AttributeError(
                f'The <class "{name}"> as a subclass of <class "_Base"> must '
                'define its __fields__ attribute')

        for attr, desc in fields.items():
            if not isinstance(desc, Descriptor):
                raise TypeError(
                    f'The attribute ({attr}) defined in __fields__ of '
                    f'<class {name}> is not an object of <class Descriptor>')

            if attr in dct.keys():
                raise AttributeError(
                    f'The attribute ({attr}) defined in __fields__ of '
                    f'<class {name}> is redefined in its __dict__, type is '
                    f'({type(dct[attr])})')

            dct[attr] = desc

        new_cls = super().__new__(cls, name, bases, dct)

        return new_cls


class _CombineMeta(ABCMeta, _MetaBase):
    ...


class _Base(metaclass=_CombineMeta):

    def __init__(self, **kwargs):

        for name, desc in self.__class__.descriptor_generator():

            value = kwargs.get(name, None)
            if value is not None:
                setattr(self, name, value)
                continue

            if desc.default:
                continue

            if desc.required:
                raise AttributeError('There is no value/default-value for '
                                     f'initializing the attribute "{name}" of '
                                     f'<class {self.__class__.__name__}')

            if not desc.required:
                continue

            else:
                setattr(self, name, desc.generate_default_value())

    @classmethod
    def descriptor_generator(cls):

        for name, desc in cls.__dict__.items():
            if isinstance(desc, Descriptor):
                yield name, desc

    def __iter__(self):

        for key, value in self.__class__.__dict__.items():
            if not isinstance(value, Descriptor):
                continue

            desc = value
            entry = getattr(self, key)

            if entry is None and not desc.required:
                continue

            if desc.compound_type is list:
                if issubclass(desc.element_type, _Base):
                    yield key, [dict(i) for i in entry]
                else:
                    yield key, entry
            elif desc.compound_type is dict:
                if issubclass(desc.element_type, _Base):
                    yield key, {k: dict(v) for k, v in entry.items()}
                else:
                    yield key, entry
            elif desc.compound_type is None:
                if issubclass(desc.element_type, _Base):
                    yield key, dict(entry)
                else:
                    yield key, entry

    @property
    def path(self):
        return self.__path__

    @abstractproperty
    def unique_id(self):
        ...

    @abstractclassmethod
    def parse(cls, *args, **kwargs):
        ...
