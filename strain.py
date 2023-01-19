import random   # non-secure random impl
import secrets  # secure -> more strain on CPU
import uuid
import numpy as np
import os

import json
import logging
import itertools
import inspect


class GlobalTabbingFilter(logging.Filter):
    delta = 0
    def filter(self, record):
        if not hasattr(self, 'delta'):
            self.delta = 0
        if not hasattr(self, 'min_stack_length'):
            self.min_stack_length = len(inspect.stack())
        record.tabs = '  ' * 2 * (len(inspect.stack()) - self.min_stack_length + self.delta)
        return True
    def add_depth(self, delta_up):
        if not hasattr(self, 'delta'):
            self.delta = 0
        self.delta += delta_up
    def remove_depth(self, delta_down):
        if not hasattr(self, 'delta'):
            self.delta = 0
        self.delta -= delta_down


global_tabbing_filter_instance = GlobalTabbingFilter()


def configure_logger(logger, logging_level=logging.DEBUG):
    logger.setLevel(logging_level)
    logger.addFilter(global_tabbing_filter_instance)
    handler = logging.StreamHandler()
    formatter = logging.Formatter('%(name)-12s | %(levelname)-8s | %(asctime)-30s | %(tabs)s %(message)s')
    handler.setFormatter(formatter)
    handler.setLevel(logging_level)
    logger.addHandler(handler)
    return logger


logger = logging.getLogger(os.path.basename(__file__))
logger = configure_logger(logger)

def log(msg):
    logger.info(msg)

def log_indent(): global_tabbing_filter_instance.add_depth(2)
def log_dedent(): global_tabbing_filter_instance.remove_depth(2)

def is_there_blob(filename):
    return os.path.exists(filename)

def delete_blob(filename):
    os.remove(filename)   

class indent():
    def __enter__(self):
         log_indent()
    def __exit__(*args):
         log_dedent()

def write_blob(filename, num_bytes_to_write: int):
    with open(filename, mode='wb') as f:
        log(f'Writing {num_bytes_to_write} bytes to "{filename}"... ')
        bytes_written = 0
        num_updates = (2 ** 3)
        blob_size = int(num_bytes_to_write / num_updates)
        while bytes_written < num_bytes_to_write:
            rand_bits = secrets.randbits(8)
            f.write(np.random.bytes(2 ** 10))
            bytes_written += 1

            if (bytes_written % blob_size) == 0:
                with indent(): log(f'. (wrote {blob_size} bytes)')
        # 
        
        with indent():
            log(f' done: wrote {num_bytes_to_write} bytes to "{filename}"')

def step():
    """
    
    [Ref: Wiki]
    https://en.wikipedia.org/wiki/Megabyte#:~:text=kilobyte-,10242,mebibyte,-MB
    
    """
    filename = os.path.join(str(uuid.uuid4()))
    
    # [Ref: https://stackoverflow.com/questions/273192/how-can-i-safely-create-a-nested-directory-in-python#:~:text=try%3A%0A%20%20%20%20os.makedirs(%22path/to/directory%22)%0Aexcept%20FileExistsError%3A%0A%20%20%20%20%23%20directory%20already%20exists%0A%20%20%20%20pass]
    # [Ref: https://stackoverflow.com/questions/5137497/find-the-current-directory-and-files-directory#:~:text=dir_path%20%3D%20os.path.dirname(os.path.realpath(__file__))]
    dirname = os.path.join(os.path.dirname(os.path.realpath(__file__)), "out")
    os.makedirs(dirname, exist_ok=True)
    filename = os.path.join(dirname, filename)

    if is_there_blob(filename):
        delete_blob(filename)
    num_bytes = 2 ** 20    # one mebibyte ~= 1gb [Ref: Wiki]
    write_blob(filename, num_bytes)

def main():
    i = 0
    num_steps = 2 ** 10   # 1024 writes and deletes of ~one megabyte each
    while True:
        log(f'Started step {i}')
        step()
        log('Done.')
        i = i + 1

if __name__ == "__main__":
    main()
