import asyncio
from androidtvremote2 import AndroidTVRemote

async def discover():
    print("Searching for Android TV devices...")
    # The library doesn't have a direct "discover" function that returns a list easily in some versions.
    # It usually uses zeroconf. 
    # Let's see if we can find how to use it.
    pass

if __name__ == "__main__":
    # asyncio.run(discover())
    print("androidtvremote2 is available.")
