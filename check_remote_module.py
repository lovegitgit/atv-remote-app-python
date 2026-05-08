import androidtvremote2.remote
import inspect

print("Constants in androidtvremote2.remote:")
for name, obj in inspect.getmembers(androidtvremote2.remote):
    if not name.startswith("_"):
        print(f"- {name}: {obj}")
