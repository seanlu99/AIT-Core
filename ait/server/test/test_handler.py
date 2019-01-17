from ait.server.handler import Handler
from nose.tools import *
import mock


class TestHandlerClassWithInputOutputTypes(object):
    handler = Handler(input_type='int', output_type='str')

    def test_handler_creation(self):
        assert self.handler.input_type is 'int'
        assert self.handler.output_type is 'str'

    def test_validate_input_types(self):
        # test successful conversions
        valid = self.handler.validate_input(2)
        assert valid == 2
        valid = self.handler.validate_input('2')
        assert valid == 2
        # test unsuccessful conversions
        with assert_raises_regexp(ValueError,
                                  'invalid literal'):
            self.handler.validate_input('a string')

    @mock.patch('ait.server.handler.Handler.handle', return_value='SpecialReturn')
    def test_execute_handler_returns_handle_return_on_input(self,
                                                                    handle_mock):
        returned = self.handler.execute_handler('2')
        assert returned == 'SpecialReturn'

    def test_execute_handler_raises_error_on_invalid_input(self):
        with assert_raises_regexp(ValueError, 'Input is not of valid type: '):
            self.handler.execute_handler('invalid input data')


class TestHandlerClassWithoutInputOutputTypes(object):
    handler = Handler()

    def test_handler_default_params(self):
        assert self.handler.input_type is None
        assert self.handler.output_type is None

    def test_validate_input_no_types(self):
        valid = self.handler.validate_input('anything')
        assert valid == 'anything'

    def test_handle_raises_not_implemented_error(self):
        with assert_raises_regexp(NotImplementedError,
                                  ('This handle method must be implemented '
                                   'by a custom handler class that inherits '
                                   'from this abstract Handler. This abstract '
                                   'Handler class should not be instantiated.')):
            self.handler.handle('some_input')

    @mock.patch('ait.server.handler.Handler.handle', return_value='SpecialReturn')
    def test_execute_handler_returns_handle_return_on_input(self,
                                                            handle_mock):
        returned = self.handler.execute_handler('2')
        assert returned == 'SpecialReturn'

    def test_handler_repr(self):
        assert self.handler.__repr__() == '<handler.Handler>'
