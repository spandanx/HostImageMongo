import time
import functools
import logging

def retry(max_retries=3, delay=2, exceptions=(Exception,)):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            attempt = 0
            while attempt < max_retries:
                try:
                    if attempt > 0:
                        logging.info(f"Retry attempt {attempt+1}/{max_retries}")
                    return func(*args, **kwargs)
                except exceptions as e:
                    attempt += 1
                    logging.info(f"Retry {attempt}/{max_retries} failed: {e}")

                    if attempt == max_retries:
                        raise

                    time.sleep(delay)
        return wrapper
    return decorator