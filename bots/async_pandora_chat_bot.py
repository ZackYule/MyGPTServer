import asyncio
from webs.async_pandora import Login2Page, ChatPage
from playwright.async_api import async_playwright
import uuid
import logging
from logger_config import setup_logging

logger = logging.getLogger(__name__)


class PandoraChatManager:
    _instance = None  # 单例实例

    def __init__(self):
        self.playwright = None
        self.browser = None
        self.chat_pages = {}

    @classmethod
    async def create(cls):
        if cls._instance is None:
            cls._instance = cls()
            await cls._instance.initialize_resources()
        return cls._instance

    async def initialize_resources(self):
        try:
            self.playwright = await async_playwright().start()
            self.browser = await self.playwright.chromium.launch(headless=False
                                                                 )
        except Exception as e:
            logger.error(f"资源初始化失败: {e}")

    async def start_conversation(self):
        try:
            login_context = await Login2Page.create(self.browser)
            login_page = await login_context.get_new_page()
            chat_page = await ChatPage.create(login_page)
            page_id = uuid.uuid4().hex[:6]
            self.chat_pages[page_id] = chat_page
            return (page_id, chat_page)
        except Exception as e:
            logger.error(f"对话启动失败: {e}")
            return None

    async def end_all_conversations(self):
        try:
            if self.browser:
                await self.browser.close()
                self.browser = None
            if self.playwright:
                await self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.error(f"结束全部对话时发生错误: {e}")


class PandoraChatBot:
    chat_manager = None  # 单例将在 create 方法中初始化

    def __init__(self, chat_page, page_id):
        self.id = page_id
        self.chat_page = chat_page

    @classmethod
    async def create(cls):
        if cls.chat_manager is None:
            cls.chat_manager = await PandoraChatManager.create()

        # 从 PandoraChatManager 单例中异步获取 page_id 和 chat_page
        try:
            page_id, chat_page = await cls.chat_manager.start_conversation()
            # await chat_page.switch_to_GPT4()
            return cls(chat_page, page_id)
        except Exception as e:
            logger.error(f"新建会话机器人时发生错误: {e}")

    async def send_message(self, message):
        try:
            await self.chat_page.ask(message)
        except Exception as e:
            logger.error(f"发送消息时出错: {e}")

    async def receive_message(self):
        try:
            return await self.chat_page.get_answer()
        except Exception as e:
            logger.error(f"接收消息时出错: {e}")
            return None
