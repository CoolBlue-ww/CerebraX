from pydantic import BaseModel
import httpx

class C(BaseModel):
    a: dict[str, httpx.Client]

b = C(a={"q": httpx.Client()})
print(b)