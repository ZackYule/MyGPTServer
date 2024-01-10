import sys
from pathlib import Path

current_dir = Path(__file__).resolve().parent
project_root = current_dir.parent
sys.path.append(str(project_root))

from webs.async_pandora import Login2Page, ChatPage
from playwright.async_api import async_playwright
import logging
from config_manager import get_config
from logger_config import setup_logging
import asyncio

logger = logging.getLogger(__name__)


async def get_gpt4_ready(playwright) -> None:
    browser = await playwright.chromium.launch(headless=False)
    login_context = await Login2Page.create(browser)
    page = await login_context.get_new_page()
    chat_page = await ChatPage.create(page)
    await chat_page.switch_to_GPT4_Mobile()
    return chat_page


async def test_pandora():
    async with async_playwright() as playwright:
        chat_page = await get_gpt4_ready(playwright)

        while True:
            query = input('human:')
            # query = '修改以下内容中的错别字，写在一行给我：' + '\n' + query
            await chat_page.ask(query)

            async for answer_chunk in chat_page.get_answer_streaming():
                logger.info(answer_chunk)

            print(await chat_page.get_answer(text_format='markdown'))


if __name__ == "__main__":
    asyncio.run(test_pandora())
