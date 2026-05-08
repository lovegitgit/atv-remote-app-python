import androidtvremote2
import inspect

print("Classes in androidtvremote2:")
for name, obj in inspect.getmembers(androidtvremote2):
    if inspect.isclass(obj):
        print(f"- {name}")

from androidtvremote2 import AndroidTVRemote
print("\nMethods in AndroidTVRemote:")
for name, obj in inspect.getmembers(AndroidTVRemote):
    if not name.startswith("_"):
        print(f"- {name}")
