from imgrass_horizon.lib.object import (
    Descriptor, DescriptorSyntaxError, DescriptorRuntimeError
)


class TestDescriptor(object):

    def test_valid_descriptors(self):

        class Demo:
            count = Descriptor(int)
