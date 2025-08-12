# meta developer: @byebyeskype
# scope: hikka_only

import asyncio
import random
import aiohttp
from .. import loader, utils
from telethon import errors

@loader.tds
class AutoSpamOnlineMod(loader.Module):
    """Автоспам с фразами из TXT на GitHub + рандомная задержка"""

    strings = {
        "name": "AutoSpamOnline",
        "spam_started": "🚀 <b>Онлайн-спам запущен!</b>",
        "spam_stopped": "⛔ <b>Спам остановлен</b>",
        "error_download": "❌ <b>Ошибка загрузки фраз:</b> <code>{}</code>",
        "error_no_messages": "❌ <b>В удалённом файле нет сообщений!</b>",
        "already_running": "⚠️ <b>Спам уже запущен</b>",
        "not_running": "❌ <b>Спам не активен</b>"
    }

    def __init__(self):
        self.spam_active = False
        # Правильный RAW URL
        self.url = "https://raw.githubusercontent.com/saltviper3333/gdfsfdsfdsf/main/messages.txt"

    async def get_messages(self):
        """Скачать TXT-файл и вернуть список строк"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        text_data = await response.text()
                        return [line.strip() for line in text_data.splitlines() if line.strip()]
                    else:
                        return None
        except Exception as e:
            return str(e)

    @loader.command()
    async def startspam(self, message):
        """Запустить онлайн-спам"""
        if self.spam_active:
            await utils.answer(message, self.strings["already_running"])
            return

        phrases = await self.get_messages()
        if phrases is None:
            await utils.answer(message, self.strings["error_download"].format("HTTP error"))
            return
        if isinstance(phrases, str):
            await utils.answer(message, self.strings["error_download"].format(phrases))
            return
        if not phrases:
            await utils.answer(message, self.strings["error_no_messages"])
            return

        self.spam_active = True
        await utils.answer(message, self.strings["spam_started"])

        try:
            while self.spam_active:
                text = random.choice(phrases)
                try:
                    await message.client.send_message(message.chat_id, text)
                    await asyncio.sleep(random.uniform(0.08, 0.5))  # ↓ задержка снижена
                except errors.FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    break
        finally:
            self.spam_active = False

    @loader.command()
    async def stopspam(self, message):
        """Остановить спам"""
        if self.spam_active:
            self.spam_active = False
            await utils.answer(message, self.strings["spam_stopped"])
        else:
            await utils.answer(message, self.strings["not_running"])
