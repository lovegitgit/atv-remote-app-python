import androidtvremote2
from androidtvremote2 import AndroidTVRemote
import inspect

print("Methods in AndroidTVRemote:")
for name, obj in inspect.getmembers(AndroidTVRemote):
    if not name.startswith("_"):
        print(f"- {name}")
