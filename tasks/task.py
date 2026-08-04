from abc import ABC

class Task(ABC):
    name = ""

    def check(self):
        raise NotImplementedError

    def execute(self):
        raise NotImplementedError
