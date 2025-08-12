import asyncio
import random
import aiohttp
from .. import loader, utils
from telethon import events, errors


@loader.tds
class AutoSpamOnlineMod(loader.Module):
    """Автоспам с фразами из облачного TXT файла + автобайт по .q"""

    strings = {
        "name": "AutoSpamOnline",
        "spam_started": "🚀 <b>ебля запущена!</b>",
        "spam_stopped": "⛔ <b>ебля остановлена</b>",
        "error_download": "❌ <b>Ошибка загрузки фраз:</b> <code>{}</code>",
        "error_no_messages": "❌ <b>В удалённом файле нет сообщений!</b>",
        "already_running": "⚠️ <b>ебля уже запущена</b>",
        "not_running": "❌ <b>ебля не активна</b>",
        "q_no_reply": "⚠️ <b>Используй эту команду в ответ на сообщение!</b>",
        "q_added": "✅ <b>Автобайт на {}</b>",
        "qq_done": "🗑 <b>Все автобайты остановлены</b>",
    }

    def __init__(self):
        self.spam_active = False
        self.q_targets = {}  # chat_id: set(user_ids)
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

    # === обычный спам ===
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

    # === автобайт .q / .qq ===
    @loader.command()
    async def q(self, message):
        """В ответ на сообщение — добавить юзера в список автоответа"""
        if not message.is_reply:
            await utils.answer(message, self.strings["q_no_reply"])
            return

        reply_msg = await message.get_reply_message()
        target_id = reply_msg.sender_id
        chat_id = message.chat_id

        if chat_id not in self.q_targets:
            self.q_targets[chat_id] = set()
        self.q_targets[chat_id].add(target_id)

        user_name = utils.get_display_name(reply_msg.sender)
        await utils.answer(message, self.strings["q_added"].format(user_name))
        await asyncio.sleep(2)
        await message.delete()

    @loader.command()
    async def qq(self, message):
        """Остановить все автобайты"""
        self.q_targets.clear()
        await utils.answer(message, self.strings["qq_done"])

    @loader.loop(interval=0.5, autostart=True)
    async def _check_q_targets(self):
        """Слушаем чат и отвечаем по шаблону на сообщения от выбранных пользователей"""
        if not self.q_targets:
            return  # никого не байтим

        phrases = await self.get_messages()
        if not phrases or isinstance(phrases, str):
            return

        async for event in self.client.iter_messages(None, limit=1):
            pass  # нужен для инициализации соединения в loop

    @loader.handler()
    async def watcher(self, message):
        chat_id = message.chat_id
        from_id = getattr(message.sender, 'id', None)

        if chat_id in self.q_targets and from_id in self.q_targets[chat_id]:
            # выбираем случайную фразу из шаблона
            phrases = await self.get_messages()
            if not phrases or isinstance(phrases, str):
                return
            text = random.choice(phrases)
            try:
                await message.reply(text)
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
                await message.reply(text)
