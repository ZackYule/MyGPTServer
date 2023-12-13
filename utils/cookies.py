import json
import aiofiles


def save_cookies(context, path):
    with open(path, "w") as file:
        json.dump(context.cookies(), file)


def load_cookies(context, path):
    with open(path, "r") as file:
        cookies = json.load(file)
        context.add_cookies(cookies)


async def async_save_cookies(context, path):
    cookies = await context.cookies()
    async with aiofiles.open(path, "w") as file:
        await file.write(json.dumps(cookies))


async def async_load_cookies(context, path):
    async with aiofiles.open(path, "r") as file:
        cookies = json.loads(await file.read())
        await context.add_cookies(cookies)
