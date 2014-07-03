"""
Tool for measuring performance
"""
try:
    from time import process_time as time_source
except ImportError:
    from time import clock as time_source

def measure(s, cycles):
    def out(func):
        def wrapper(*args):
            start = time_source()
            func(*args)
            passed = time_source() - start
            print("Finished {0} cycles for {1} in {2:0.5f} seconds".
                  format(cycles, s, passed))
        return wrapper
    return out