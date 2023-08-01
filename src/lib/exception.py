from sys import modules as SYS_MODULES


class ExceptionInfo(object):
    __MESSAGE__ = None
    __FUNCTION__ = None

    def validate_self(self):
        return isinstance(self.__MESSAGE__, str) and \
                isinstance(self.__FUNCTION__, str)

    def tell_me(self, message):
        self.__MESSAGE__ = message

    def get_message(self):
        assert self.__MESSAGE__ is not None
        return self.__MESSAGE__

    def get_function(self):
        return self.__FUNCTION__

    def set_function(self, function_name):
        self.__FUNCTION__ = function_name


class ExceptionBase(Exception):
    '''
    When defining exceptions, we usually create an exception class for each
    case, but this can sometimes seem trival. But if we do not do this, many
    different situations are indistinguishable. For example: File access error,
    it may be that the file does not exist, or it may be unreadable. We want to
    define it with the following way:

        >>> class FileAccessError(ExceptionBase):

        >>>     @register_exception
        >>>     def not_exist(info, ...):
        >>>         info.tell_me(...)

        >>>     @register_exception
        >>>     def unreadable(info, ...):
        >>>         info.tell_me(...)
        >>>         info.x = 1

        >>> try:
        >>>     raise FileAccessError.unreadable(...)
        >>> except FileAccessError as e:
        >>>     if e.info.x == 1:
        >>>         ...

    As the above example implies, both functions <not_exist> and <unreadable>
    are written as independent function rather than method("self" or "cls" are
    not needed). The decorator <register_exception> would be responsible for
    transforming it into a function that returns the corresponding exception
    instance, and the information of this exception instance is passed by the
    first formal parameter <info>, which is an instance of class
    <<ExceptionInfo>> for storing data. As statement "info.x = 1" implies, we
    can add custom attributes to this instance, so that custom information can
    be passed to the exception catcher.
    '''

    def __init__(self, info: ExceptionInfo):
        assert isinstance(info, ExceptionInfo)
        assert info.validate_self()

        self._info = info
        super().__init__(info.get_message())
        self.function = info.get_function()

    @property
    def info(self):
        return self._info


def register_exception(func):

    def wrapper(*args, **kwargs):
        assert func.__class__.__name__ == 'function'

        qual_names = func.__qualname__.split('.')
        module_name = func.__module__
        # The decorator will only decorate the first-level functions under
        # the first-level class.
        assert len(qual_names) == 2

        class_name, func_name = qual_names
        cls = getattr(SYS_MODULES[module_name], class_name)

        info = ExceptionInfo()
        func(info, *args, **kwargs)
        info.set_function(func_name)

        return cls(info)

    return wrapper


__all__ = ('ExceptionBase', 'register_exception')
