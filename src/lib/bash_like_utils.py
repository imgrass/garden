from .exception import ExceptionBase, ExceptionInfo, register_exception
import os
import os.path as os_path


class FileException(ExceptionBase):

    @register_exception
    def file_not_found(info: ExceptionInfo, path):
        info.tell_me(f'The file {path} is not found')


def is_writable_file(path):

    if ...
