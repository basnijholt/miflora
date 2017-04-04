import time
import logging

LOGGER = logging.getLogger(__name__)


def retry(retries=3, exception=Exception, delay=None, on_exception=None):
    """
    Retry decorator
    :param retries: number of retries to perform
    :param exception: Exception, or tuple thereof, to catch
    :param delay: function returning sleeping time [s] between tries
    :param on_exception: callback executed on exception
    :return:
    """
    def _decorator(func):
        def _wrapper(*args, **kwargs):
            ex = None
            for i in range(retries+1):
                try:
                    return func(*args, **kwargs)
                except exception as e:
                    ex = e
                    if on_exception is not None:
                        on_exception(e)
                if delay is not None:
                    time.sleep(delay(i))
            else:
                raise ex
        return _wrapper
    return _decorator


def auto_connect(func):
    """
    Automatic connection decorator
    Ensures that a connection is established if it is not already done
    """
    def _wrapper(self, *args, **kwargs):
        if not self.connected:
            with self:
                return func(self, *args, **kwargs)
        else:
            return func(self, *args, **kwargs)
    return _wrapper


def cached_ttl(ttl):
    """
    Simple timed cache decorator implementation
    Keeps track of time and caller arguments
    :param ttl: cache time to live [s]
    :return:
    """
    def _decorator(func):
        cache = None
        timestamp = 0
        function_args = None

        def _wrapper(*args, **kwargs):
            nonlocal timestamp
            nonlocal function_args
            nonlocal cache
            now = time.time()
            if cache is not None and (now - timestamp) < ttl and function_args == (args, kwargs):
                LOGGER.debug("Cache returned for %s" % func)
                return cache
            else:
                timestamp = now
                function_args = (args, kwargs)
                cache = func(*args, **kwargs)
                return cache
        return _wrapper
    return _decorator
