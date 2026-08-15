class Greeter:
    message = "hello"

    def greet(self, name):
        return f"{self.message}, {name}"


def build_greeter():
    greeter = Greeter()
    return greeter
