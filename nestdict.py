class nestdict():
    def __init__(self, di):
        for x in di.keys():
            setattr(self, x, di[x])

c = nestdict({'p1':'v1','p2':'v2'})
print(c.p2)