"""Execution related tool mixins
"""

# Ben Peters (bencpeters@gmail.com)

from concurrent.futures import ThreadPoolExecutor

class ThreadedExecutor(object):
    """Mixin to execute a specified function in a separate thread.
    """
    def __init__(self):
        super(ThreadedExecutor, self).__init__()
        self._executor = None

    @property
    def executor(self):
        if self._executor is None:
            self._executor = ThreadPoolExecutor(1)
        return self._executor

    def execute(self, fxn, cb, *args, **kwargs):
        """Execute the exec_function in the threaded executor. Unless running
        synchronously, this function call returns immediately, but registers
        the supplied callback function to be run on async execution completion.

        :param fxn: Function to be run in thread executor.
        :param cb: Callback function to be run when threaded function is done.
                   Receives the return value of the executed function as the
                   sole argument.
        :param run_sync: Boolean flag to run function synchronously. Defaults to
                         False.
        """
        future = self.executor.submit(fxn, args, kwargs)

        if 'run_sync' in kwargs and kwargs['run_sync']:
            values = future.result()
            cb(values)
        else:
            cb_wrapper = lambda f: cb(f.result())
            future.add_done_callback(cb_wrapper)

        return future
