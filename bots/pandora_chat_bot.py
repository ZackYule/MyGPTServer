from playwright.sync_api import sync_playwright
from webs.pandora import Login2Page, ChatPage
import uuid
import logging
from logger_config import setup_logging

logger = logging.getLogger(__name__)


class PandoraChatManager:
    _instance = None  # 单例实例
    playwright = None  # Playwright 实例
    browser = None  # 浏览器实例
    chat_pages = {}  # 聊天页面字典

    def __new__(cls):
        # 单例模式，确保只创建一个实例
        if cls._instance is None:
            cls._instance = super(PandoraChatManager, cls).__new__(cls)
            cls.initialize_resources()
        return cls._instance

    @classmethod
    def initialize_resources(cls):
        # 初始化 Playwright 和浏览器
        try:
            cls.playwright = sync_playwright().start()
            cls.browser = cls.playwright.chromium.launch(headless=True)
        except Exception as e:
            logger.error(f"资源初始化失败: {e}")

    def start_conversation(self):
        # 启动新的对话
        try:
            page = Login2Page(self.browser).get_new_page()
            chat_page = ChatPage(page)
            page_id = uuid.uuid4().hex[:6]
            self.chat_pages[page_id] = chat_page
            return (page_id, chat_page)
        except Exception as e:
            logger.error(f"对话启动失败: {e}")
            return None

    def end_all_conversations(self):
        # 结束所有对话
        try:
            if self.browser:
                self.browser.close()
                self.browser = None
            if self.playwright:
                self.playwright.stop()
                self.playwright = None
        except Exception as e:
            logger.error(f"结束全部对话时发生错误: {e}")


class PandoraChatBot:
    chat_manager = PandoraChatManager()  # 获取单例

    def __init__(self):
        # 直接从 PandoraChatManager 单例中获取 page_id 和 chat_page
        self.id, self.chat_page = PandoraChatBot.chat_manager.start_conversation(
        )
        # self.chat_page.switch_to_GPT4()

    def send_message(self, message):
        try:
            self.chat_page.ask(message)
        except Exception as e:
            logger.error(f"发送消息时出错: {e}")

    def receive_message(self):
        try:
            return self.chat_page.get_answer()
        except Exception as e:
            logger.error(f"接收消息时出错: {e}")
            return None
