from . import creds

import aiohttp
import asyncio
from asusrouter import AsusRouter, AsusData


# Create a new event loop
loop = asyncio.new_event_loop()

# Create aiohttp session
session = aiohttp.ClientSession(loop=loop)

router = AsusRouter(  # required - both IP and URL supported
    hostname=f"{creds.hostname()}",  # required
    username=f"{creds.username()}",  # required
    password=f"{creds.password()}",  # required
    use_ssl=True,  # optional
    session=session,  # optional
)

# Connect to the router
loop.run_until_complete(router.async_connect())

# Now you can use the router object to call methods
data = loop.run_until_complete(router.async_get_data(AsusData.NETWORK))
print(data)

# Remember to disconnect and close the session when you're done
loop.run_until_complete(router.async_disconnect())
loop.run_until_complete(session.close())

if __name__ == "__main__":
    pass
