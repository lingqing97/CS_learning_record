import multiprocessing as mp
import time,os

def say_hi(words):
    print("I say:{}".format(words))
    time.sleep(2)


class MyProcess(mp.Process):
    def __init__(self,name):
        super().__init__()
        self._name=name
    def run(self):
        print("%s is running"%self._name)
        time.sleep(2)
        print("%s is done"%self._name)


def task():
    print("%s is running,parent id is <%s>"%(os.getpid(),os.getppid()))
    time.sleep(2)
    print("ts is done,parent id is <%s>"%(os.getpid(),os.getppid()))