from webs.pandora import Login2Page, ChatPage
from playwright.sync_api import sync_playwright, Page
import logging
from config_manager import get_config
from logger_config import setup_logging

logger = logging.getLogger(__name__)


def get_gpt4_ready(playwright) -> None:

    browser = playwright.chromium.launch(headless=True)
    page = Login2Page(browser).get_new_page()

    chat_page = ChatPage(page)

    # chat_page.switch_to_GPT4()

    return chat_page


def test_pandora():

    with sync_playwright() as playwright:
        chat_page = get_gpt4_ready(playwright)

        while True:
            query = input('human:')
            # query = '修改以下内容中的错别字，写在一行给我：' + '\n' + query
            chat_page.ask(query)

            for answer_chunk in chat_page.get_answer_streaming():
                logger.info(answer_chunk)

            print(chat_page.get_answer(text_format='markdown'))


if __name__ == "__main__":
    test_pandora()
