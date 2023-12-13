import asyncio
from bots.async_pandora_chat_bot import PandoraChatBot
import logging
from logger_config import setup_logging

logger = logging.getLogger(__name__)


async def test_chat_bot():
    # 创建一个 ChatBot 实例
    bot = await PandoraChatBot.create()
    logger.info(bot.id)

    # 发送消息
    await bot.send_message("Hello, World!")

    # 接收消息
    received_message = await bot.receive_message()
    logger.info(f"Received message: {received_message}")

    bot2 = await PandoraChatBot.create()
    logger.info(bot2.chat_manager == bot.chat_manager)

    await bot.chat_manager.end_all_conversations()

    await bot.send_message("Hello, World!")
    # 接收消息
    received_message = await bot.receive_message()
    logger.info(f"Received message: {received_message}")


# 运行测试
asyncio.run(test_chat_bot())
