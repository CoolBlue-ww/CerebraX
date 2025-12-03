# import requests
#
# url = "http://127.0.0.1:8000/shutdown"
#
# data = {
#     "shutdown": True,
#     "wait": 1
# }
#
# response = requests.post(url, json=data)
# print(response.json())
# def t():
#     import requests
#     url = "https://www.baidu.com/"
#     response = requests.get(url)
#     return response.text
#
# import pickle
#
# d = pickle.dumps(t)
# print(pickle.loads(d)())


class T(object):
    def __init__(self):
        self._a = 90

    def a_a(self):
        return self._a

import pickle, base64

t = T()

b = base64.b64encode(pickle.dumps(t))
print(type(b.decode("ascii")))
print(b.decode("ascii"))

