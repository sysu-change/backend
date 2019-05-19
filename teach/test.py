def test(**kwargs):
    print(kwargs)
    for i in kwargs.items():
        print(i)

test(a = 1, b = 2, c = 3)