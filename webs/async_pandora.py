import os
import asyncio
from playwright.async_api import Page, Browser, BrowserContext, Locator
import html2text
from config_manager import get_config
from utils.cookies import async_load_cookies, async_save_cookies


class Login2Page:

    URL = get_config('pandora_url')

    def __init__(self, context: BrowserContext) -> None:
        self.context = context

    @classmethod
    async def create(cls, browser: Browser):
        context = await browser.new_context(
            user_agent=
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            viewport={
                'width': 1280,
                'height': 720
            },
            extra_http_headers={
                "Accept": "text/event-stream",
                "Accept-Language": "en-US",
                "Content-Type": "application/json",
                "Referer": "http://127.0.0.1",
                "Sec-Ch-Ua":
                "\"Not_A Brand\";v=\"8\", \"Chromium\";v=\"120\", \"Google Chrome\";v=\"120\"",
                "Sec-Ch-Ua-Mobile": "?0",
                "Sec-Ch-Ua-Platform": "\"macOS\""
            })
        return cls(context)

    async def logging(self, token: str) -> Page:
        page = await self.context.new_page()
        await page.goto(self.URL, wait_until="load")

        token_button = page.get_by_role("button",
                                        name="Continue with Access Token")
        token_input = page.get_by_placeholder("Please input (access / share")
        token_enter_button = page.get_by_role("button", name="OK")

        await token_button.click()
        await token_input.fill(token)
        await token_enter_button.click()

        return page

    async def save_cookies(self, path="pandora_cookies.json") -> None:
        await async_save_cookies(self.context, path)

    async def get_new_page(self, path="pandora_cookies.json") -> Page:
        if os.path.exists(path):
            await async_load_cookies(self.context, path)
            page = await self.context.new_page()
        else:
            token = get_config('pandora_token')
            assert token != ""
            page = await self.logging(token)
            await self.save_cookies(path)

        page.set_default_timeout(1 * 60 * 1000)
        return page


class ChatPage:
    URL = get_config('pandora_url')
    answer_delay = get_config('answer_delay')

    def __init__(self, page: Page, toggle_button, GPT4_button, ask_input,
                 send_button, playwright):
        self.page = page
        self.toggle_button = toggle_button
        self.GPT4_button = GPT4_button
        self.ask_input = ask_input
        self.send_button = send_button
        self.playwright = playwright
        self.answer_delay = get_config('answer_delay')
        self.markdown_converter = html2text.HTML2Text()
        self.conversation_turn = 1

    @classmethod
    async def create(cls, page: Page, playwright: any):
        await page.goto(cls.URL, wait_until="load")
        toggle_button = page.locator('css=[id^=radix-]')
        GPT4_button = page.get_by_role("menuitem",
                                       name="GPT-4 With DALL·E, browsing")
        ask_input = page.get_by_placeholder("Message ChatGPT…")
        send_button = page.get_by_test_id("send-button")
        await page.wait_for_selector("text=Alpha", state="visible")
        # await asyncio.sleep(cls.answer_delay)
        return cls(page, toggle_button, GPT4_button, ask_input, send_button,
                   playwright)

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

    async def is_answer_stop(self) -> bool:
        if await self.page.query_selector(
                self.result_conversation_container_selector):
            return True
        return False

    async def switch_to_GPT4(self) -> None:
        await self.toggle_button.click()
        await self.GPT4_button.click()

    async def ask(self, content: str) -> None:
        await self.ask_input.fill(content)
        # await asyncio.sleep(self.answer_delay)
        await self.send_button.click()
        self.conversation_turn += 2

    async def get_answer(self, text_format='text') -> str:
        result_box = self.page.locator(
            self.result_conversation_container_selector)
        answer_el = result_box.locator('[data-message-id] .markdown')
        if text_format == 'markdown':
            return self.markdown_converter.handle(await answer_el.inner_html())
        return await answer_el.inner_text()

    async def get_real_time_answer(self, text_format='text') -> str:
        real_time_answer_el = self.realtime_conversation_element
        if text_format == 'markdown':
            return await self.markdown_converter.handle(
                await real_time_answer_el.inner_html())
        return await real_time_answer_el.inner_text()

    async def get_answer_streaming(self, text_format='text'):
        real_time_answer_el = self.realtime_conversation_element
        try:
            while not await self.is_answer_stop():
                if text_format == 'markdown':
                    yield await self.markdown_converter.handle(
                        await real_time_answer_el.inner_html())
                else:
                    yield await real_time_answer_el.inner_text()

                await asyncio.sleep(self.answer_delay)

        except Exception as e:
            yield f"Error occurred: {str(e)}"
