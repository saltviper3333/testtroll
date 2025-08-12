import asyncio
import random
import aiohttp
from .. import loader, utils
from telethon import errors


@loader.tds
class AutoSpamOnlineMod(loader.Module):
    """Автоспам + автоответ одним сообщением по шаблону"""

    strings = {
        "name": "AutoSpamOnline",
        "spam_started": "🚀 <b>ебля запущена!</b>",
        "spam_stopped": "⛔ <b>ебля остановлена</b>",
        "error_download": "❌ <b>Ошибка загрузки фраз:</b> <code>{}</code>",
        "error_no_messages": "❌ <b>В удалённом файле нет сообщений!</b>",
        "already_running": "⚠️ <b>ебля уже запущена</b>",
        "not_running": "❌ <b>ебля не активна</b>",
        "q_no_reply": "⚠️ <b>Используй эту команду в ответ на сообщение!</b>",
        "q_done": "✅ <b>Ответ отправлен</b>",
        "qq_done": "🗑 <b>Все задачи .q остановлены</b>",
    }

    def __init__(self):
        self.spam_active = False
        self.q_tasks = []  # сюда будем складывать задачи .q
        self.url = "https://raw.githubusercontent.com/saltviper3333/gdfsfdsfdsf/main/messages.txt"

    async def get_messages(self):
        """Скачивание TXT и превращение в список строк"""
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

    # === Основной спам (.sex / .s) ===
    @loader.command()
    async def sex(self, message):
        """Запустить еблю (онлайн-спам)"""
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
                    await asyncio.sleep(random.uniform(0.08, 0.5))
                except errors.FloodWaitError as e:
                    await asyncio.sleep(e.seconds)
                except Exception:
                    break
        finally:
            self.spam_active = False

    @loader.command()
    async def s(self, message):
        """Остановить еблю"""
        if self.spam_active:
            self.spam_active = False
            await utils.answer(message, self.strings["spam_stopped"])
        else:
            await utils.answer(message, self.strings["not_running"])

    # === Новый функционал .q / .qq ===
    @loader.command()
    async def q(self, message):
        """Отправить 1 случайное сообщение из шаблона как ответ"""
        if not message.is_reply:
            await utils.answer(message, self.strings["q_no_reply"])
            return

        reply_msg = await message.get_reply_message()
        phrases = await self.get_messages()
        if not phrases:
            await utils.answer(message, self.strings["error_no_messages"])
            return

        async def send_reply():
            try:
                text = random.choice(phrases)
                await message.client.send_message(
                    message.chat_id,
                    text,
                    reply_to=reply_msg.id
                )
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception:
                pass

        task = asyncio.create_task(send_reply())
        self.q_tasks.append(task)

        await message.delete()  # удаляем саму команду .q

    @loader.command()
    async def qq(self, message):
        """Остановить все активные задачи от .q"""
        for task in self.q_tasks:
            if not task.done():
                task.cancel()
        self.q_tasks.clear()
        await utils.answer(message, self.strings["qq_done"])
