import androidtvremote2
from androidtvremote2 import AndroidTVRemote
import inspect

print("async_connect signature:", inspect.signature(AndroidTVRemote.async_connect))
print("send_key_command signature:", inspect.signature(AndroidTVRemote.send_key_command))
