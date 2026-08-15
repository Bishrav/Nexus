def helper():
    return 1


def recursive(value):
    if value:
        return recursive(value - 1)
    return 0


def main():
    helper()
    service.run()
