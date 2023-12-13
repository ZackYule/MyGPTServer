from bots.pandora_chat_bot import PandoraChatBot
import logging
from logger_config import setup_logging


logger = logging.getLogger(__name__)

def test_chat_bot():
    # 创建一个 ChatBot 实例
    bot = PandoraChatBot()
    logger.info(bot.id)
    # 发送消息
    bot.send_message("Hello, World!")

    # 接收消息
    received_message = bot.receive_message()
    logger.info(f"Received message: {received_message}")
    
    bot2 = PandoraChatBot()
    logger.info(bot2.chat_manager == bot.chat_manager)

    bot.chat_manager.end_all_conversations()

    bot.send_message("Hello, World!")
    # 接收消息
    received_message = bot.receive_message()
    logger.info(f"Received message: {received_message}")

# 运行测试
test_chat_bot()
