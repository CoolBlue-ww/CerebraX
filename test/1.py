from dataclasses import dataclass

@dataclass
class Test:
    pass

a = Test()
print(a)
print(Test)
a.e = 2
print(a.e)

