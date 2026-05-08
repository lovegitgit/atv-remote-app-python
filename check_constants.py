import androidtvremote2
from androidtvremote2 import AndroidTVRemote
import inspect

# Try to find direction constants
print("Constants in androidtvremote2:")
for name, obj in inspect.getmembers(androidtvremote2):
    if not name.startswith("_"):
        print(f"- {name}: {obj}")

# Also check for any submodules or enums
