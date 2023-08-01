from imgrass_horizon.lib.exception import ExceptionBase, register_exception
from logging import getLogger


LOG = getLogger(__name__)


class ExceptionTest(ExceptionBase):

    @register_exception
    def this_is_an_error(info, arg1, arg2):
        info.tell_me(f'This is an error: arg1 = {arg1}, arg2 = {arg2}')
        info.arg1 = arg1


class TestExceptionBase(object):

    def test_normal_defined_exception(self):
        arg1 = 'jasmine'
        arg2 = 'gardenia'
        try:
            raise ExceptionTest.this_is_an_error(arg1, arg2)
        except Exception as e:
            assert isinstance(e, ExceptionBase)
            assert str(e) == f'This is an error: arg1 = {arg1}, arg2 = {arg2}'
            assert e.info.arg1 == arg1
            assert not hasattr(e.info, 'arg2')
