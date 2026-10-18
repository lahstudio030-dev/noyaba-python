x = 4
ref y = x
y = 20
view(x)

frozen_value: int = 12

func factorial(n):
    if n <= 1:
        return 1
    return n * factorial(n - 1)
view(factorial(5))

with:
    temporary = 10

with make:
    x = 10
    return x
view(make())

view("OK")
