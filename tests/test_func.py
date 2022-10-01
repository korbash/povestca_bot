def fun(a, b=4, c=8, d=9):
    print('a:', a, 'b:', b, 'c:', c, 'd:', d)


args = {'a': 1, 'b': 2, 'c': 3}
args2 = {'a': 1, 'b': 2}
args3 = {'b': 2, 'c': 3}
args4 = {}
fun(4, **args4)