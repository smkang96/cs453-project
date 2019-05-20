class C():
    def __init__(self):
        pass

    def f(self, a, b):
        if a == b:
            print("equal")
            return a
        if a > b:
            return a
        else:
            return b
