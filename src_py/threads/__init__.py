from queue import Queue, Empty
import threading


Thread = threading.Thread

STOP = object()
FINISH = object()
_wq = None
_use_workers = 0
MAX_WORKERS_TO_TEST = 64


def init(number_of_workers=0):
    global _wq, _use_workers
    if number_of_workers:
        _use_workers = number_of_workers
    else:
        _use_workers = benchmark_workers()
    _wq = WorkerQueue(_use_workers)


def quit():
    global _wq, _use_workers
    _wq.stop()
    _wq = None
    _use_workers = False


def benchmark_workers(a_bench_func=None, the_data=None):
    import pygame
    import pygame.transform
    import time

    if not a_bench_func:
        def doit(x):
            return pygame.transform.scale(x, (544, 576))
    else:
        doit = a_bench_func
    if not the_data:
        thedata = [pygame.Surface((155, 155), 0, 32) for x in range(10)]
    else:
        thedata = the_data
    best = time.time() + 100000000
    best_number = 0
    for num_workers in range(0, MAX_WORKERS_TO_TEST):
        wq = WorkerQueue(num_workers)
        t1 = time.time()
        for _ in range(20):
            print(f"active count:{threading.active_count()}")
            tmap(doit, thedata, worker_queue=wq)
        t2 = time.time()
        wq.stop()
        total_time = t2 - t1
        print(f"total time num_workers:{num_workers}: time:{total_time}:")
        if total_time < best:
            best_number = num_workers
            best = total_time
        if num_workers - best_number > 1:
            break
    return best_number


class WorkerQueue:
    def __init__(self, num_workers=20):
        self.queue = Queue()
        self.pool = []
        self._setup_workers(num_workers)

    def _setup_workers(self, num_workers):
        self.pool = []
        for _ in range(num_workers):
            self.pool.append(Thread(target=self.threadloop))
        for a_thread in self.pool:
            a_thread.setDaemon(True)
            a_thread.start()

    def do(self, f, *args, **kwArgs):
        self.queue.put((f, args, kwArgs))

    def stop(self):
        self.queue.put(STOP)
        for thread in self.pool:
            thread.join()

    def threadloop(self):
        while True:
            args = self.queue.get()
            if args is STOP:
                self.queue.put(STOP)
                self.queue.task_done()
                break
            try:
                args[0](*args[1], **args[2])
            finally:
                self.queue.task_done()

    def wait(self):
        self.queue.join()


class FuncResult:
    def __init__(self, f, callback=None, errback=None):
        self.f = f
        self.exception = None
        self.result = None
        self.callback = callback
        self.errback = errback

    def __call__(self, *args, **kwargs):
        try:
            self.result = self.f(*args, **kwargs)
            if self.callback:
                self.callback(self.result)
        except Exception as e:
            self.exception = e
            if self.errback:
                self.errback(self.exception)


def tmap(f, seq_args, num_workers=20, worker_queue=None, wait=True, stop_on_error=True):
    if worker_queue:
        wq = worker_queue
    else:
        if _wq:
            wq = _wq
        else:
            if num_workers == 0:
                return map(f, seq_args)
            wq = WorkerQueue(num_workers)
    if len(wq.pool) == 0:
        return map(f, seq_args)
    results = []
    for sa in seq_args:
        results.append(FuncResult(f))
        wq.do(results[-1], sa)
    if wait:
        wq.wait()
        if wq.queue.qsize():
            raise RuntimeError("buggy threadmap")
        if not worker_queue and not _wq:
            wq.stop()
            if wq.queue.qsize():
                um = wq.queue.get()
                if um is not STOP:
                    raise RuntimeError("buggy threadmap")
        if stop_on_error:
            error_ones = list(filter(lambda x: x.exception, results))
            if error_ones:
                raise error_ones[0].exception
        return (x.result for x in results)
    return [wq, results]