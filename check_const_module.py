import androidtvremote2.const
import inspect

print("Constants in androidtvremote2.const:")
for name, obj in inspect.getmembers(androidtvremote2.const):
    if not name.startswith("_"):
        print(f"- {name}: {obj}")
