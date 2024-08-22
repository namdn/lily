import inspect
from tornado.ioloop import IOLoop
import threading


class AsyncException(Exception):
    pass


class YieldBack:
    pass


class AsyncYield(YieldBack):
    def __init__(self):
        self._ioloop = None
        self._callback = None

    def __init__(self):
        super().__init__()

    def set_callback(self, ioloop, callback):
        self._ioloop = ioloop
        self._callback = callback

    def start(self):
        raise NotImplementedError("You must override this code")


class AsyncRoutine(AsyncYield):
    pass


class BigTask(AsyncYield):
    def __init__(self, func, *args, **kwargs):
        super().__init__()
        self._func = func
        self._args = args
        self._kwargs = kwargs

    def start(self):
        self._thead = threading.Thread(target=self.calculate, name="run big task")
        self._thead.start()

    def calculate(self):
        result = self._func(*self._args, **self._kwargs)
        self._ioloop.add_callback(self._callback, result)


def slowfunc(func):
    def wrapper(*args, **kwargs):
        bigtask = BigTask(func, *args, **kwargs)
        return bigtask

    return wrapper


def get_main_ioloop():
    loop = IOLoop.current()
    return loop


def start(*generators):
    loop = get_main_ioloop()
    
    for generator in generators:
        loop.add_callback(next, generator)

    loop.start()


def routine(func):
    if not inspect.isgeneratorfunction(func):
        raise AsyncException("Routine now just supports generator function only")

    class Asynchronous(AsyncRoutine):
        def __init__(self, *args, **kwargs):
            self._iterator = func(*args, **kwargs)
            self._has_value = False
            self._value = None
            self._parent = None

        def __iter__(self):
            raise AsyncException("Can not loop in `routine` function")

        def __next__(self):
            try:
                if not self._has_value:
                    yieldback = next(self._iterator)
                else:
                    value, self._has_value = self._value, False
                    yieldback = self._iterator.send(value)

                if not isinstance(yieldback, YieldBack):
                    raise AsyncException(
                        "Use `YieldBack` inherit instance after yield keyword in `routine` function"
                    )

                if isinstance(yieldback, AsyncRoutine):
                    yieldback._parent = self
                    yieldback.set_callback(get_main_ioloop(), yieldback.send)
                elif isinstance(yieldback, AsyncYield):
                    yieldback.set_callback(get_main_ioloop(), self.send)

                yieldback.start()

                return yieldback
            except StopIteration as e:
                if self._parent:
                    loop = get_main_ioloop()
                    loop.add_callback(self._parent.send, e.value)

        def start(self):
            return next(self)

        def send(self, result):
            self._value = result
            self._has_value = True
            next(self)

    return Asynchronous
