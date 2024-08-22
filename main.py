from tornado.ioloop import IOLoop
import lily


@lily.slowfunc
def prime_factorization(n):
    divisor = 2
    factors = []
    while n > 1:
        while n % divisor == 0:
            n //= divisor
            factors.append(divisor)
        divisor += 1

    return factors


@lily.routine
def fibonacci(n):
    if n <= 2:
        return 1
    a = yield fibonacci(n-1)
    b = yield fibonacci(n-2)
    return a + b


@lily.routine
def test1():
    a = yield prime_factorization(2108821011)
    print(a)


@lily.routine
def test2():
    f = yield fibonacci(25)
    print(f)


if __name__ == "__main__":
    lily.start(test1(), test2())
