import os


def helper():
    return os.getcwd()


class Service:
    def run(self):
        return helper()
