from pathlib import Path

p = Path("/usr/share/applications/").joinpath("google-chrome.desktop")
print(str(p))
with p.open(mode="r") as f:
    rs = f.read()
    print(rs)