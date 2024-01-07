import os
from playwright.sync_api import Page, BrowserContext, Locator
import time
import html2text
from config_manager import get_config
from utils.cookies import load_cookies, save_cookies


class Login2Page:

    URL = get_config('pandora_url')

    def __init__(self, browser) -> None:

        self.context: BrowserContext = browser.new_context(
            user_agent=
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={
                'width': 1280,
                'height': 720
            })

    def logging(self, token: str) -> Page:
        page = self.context.new_page()
        page.goto(self.URL, wait_until="load")

        token_button = page.get_by_role("button",
                                        name="Continue with Access Token")
        token_input = page.get_by_placeholder("Please input (access / share")
        token_enter_button = page.get_by_role("button", name="OK")

        token_button.click()
        token_input.fill(token)
        token_enter_button.click()

        return page

    def save_cookies(self, path="pandora_cookies.json") -> None:
        save_cookies(self.context, path)

    def get_new_page(self, path="pandora_cookies.json") -> Page:
        if os.path.exists(path):
            load_cookies(self.context, path)
            page = self.context.new_page()
        else:
            token = get_config('pandora_token')
            assert token != ""
            page = self.logging(token)
            self.save_cookies(path)

        return page


class ChatPage:
    URL = get_config('pandora_url')

    def __init__(self, page: Page) -> None:
        self.page = page
        self.answer_delay = get_config('answer_delay')

        self.toggle_button = self.page.locator('css=[id^=radix-]')
        self.GPT4_button = self.page.get_by_role(
            "menuitem", name="GPT-4 With DALL·E, browsing")
        self.ask_input = self.page.get_by_placeholder("Message ChatGPT…")
        self.send_button = self.page.get_by_test_id("send-button")
        self.web_logo = self.page.locator("text=Hello, PandoraNext.")

        self.markdown_converter = html2text.HTML2Text()
        self.conversation_turn = 1

        self.page.goto(self.URL, wait_until="load")
        assert self.web_logo.is_visible()

    @property
    def realtime_conversation_container_selector(self) -> str:
        assert self.conversation_turn > 1
        return f'[data-testid="conversation-turn-{self.conversation_turn}"]'

    @property
    def result_conversation_container_selector(self) -> str:
        assert self.conversation_turn > 1
        return f'xpath=//div[@data-testid="conversation-turn-{self.conversation_turn}" and count(.//button) > 1]'

    @property
    def realtime_conversation_element(self) -> Locator:
        return self.page.locator(
            self.realtime_conversation_container_selector +
            ' [data-message-id] .markdown')

    def is_answer_stop(self) -> bool:
        if self.page.query_selector(
                self.result_conversation_container_selector):
            return True
        return False

    def switch_to_GPT4(self) -> None:
        self.toggle_button.click()
        self.GPT4_button.click()

    def ask(self, content: str) -> None:
        self.ask_input.fill(content)
        self.send_button.click()
        self.conversation_turn += 2

    def get_answer(self, text_format='text') -> str:
        result_box = self.page.locator(
            self.result_conversation_container_selector)
        answer_el = result_box.locator('[data-message-id] .markdown')
        if text_format == 'markdown':
            return self.markdown_converter.handle(answer_el.inner_html())
        return answer_el.inner_text()

    def get_real_time_answer(self, text_format='text') -> str:
        real_time_answer_el = self.realtime_conversation_element
        if text_format == 'markdown':
            return self.markdown_converter.handle(
                real_time_answer_el.inner_html())
        return real_time_answer_el.inner_text()

    def get_answer_streaming(self, text_format='text') -> str:
        real_time_answer_el = self.realtime_conversation_element

        try:
            while not self.is_answer_stop():
                if text_format == 'markdown':
                    yield self.markdown_converter.handle(
                        real_time_answer_el.inner_html())
                else:
                    yield real_time_answer_el.inner_text()

                time.sleep(self.answer_delay)

        except Exception as e:
            yield f"Error occurred: {str(e)}"
