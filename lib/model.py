import os.path
import pickle
import datetime

def cacheOnDiskWithPickle(filename):
    '''
    Cache the return value of a function on disk using pickle. But invalidate
    after 20 minutes of the file timestamp.
    '''
    def decorator(func):
        def wrapper():
            try:
                print('Trying to load from cache', filename)
                with open(filename, 'rb') as f:
                    timestamp = os.path.getmtime(filename)
                    if datetime.datetime.now().timestamp() - timestamp < 20 * 60:
                        print('Cache hit')
                        return pickle.load(f)
            except Exception:
                print('Cache miss')
            result = func()
            with open(filename, 'wb') as f:
                pickle.dump(result, f)
            return result
        return wrapper
    return decorator
