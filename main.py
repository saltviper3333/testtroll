import asyncio
import random
import aiohttp
from .. import loader, utils
from telethon import errors


@loader.tds
class AutoSpamOnlineMod(loader.Module):
    """Автоспам + автобайт (.q / .qq / .qwe)"""

    strings = {
        "name": "AutoSpamOnline",
        "spam_started": "🚀 <b>ебля запущена!</b>",
        "spam_stopped": "⛔ <b>ебля остановлена</b>",
        "error_download": "❌ <b>Ошибка загрузки фраз:</b> <code>{}</code>",
        "error_no_messages": "❌ <b>В удалённом файле нет сообщений!</b>",
        "already_running": "⚠️ <b>ебля уже запущена</b>",
        "not_running": "❌ <b>ебля не активна</b>",
        "q_no_reply": "⚠️ <b>Используй эту команду ответом на сообщение!</b>",
        "q_added": "✅ <b>Байт включён на {}</b>",
        "qq_done": "🗑 <b>Все байты остановлены</b>",
        "qwe_header": "📜 <b>Активные байты:</b>\n"
    }

    def __init__(self):
        self.spam_active = False
        # {chat_id: set(user_ids)}
        self.q_targets = {}
        self.url = "https://raw.githubusercontent.com/saltviper3333/gdfsfdsfdsf/main/messages.txt"

    async def get_messages(self):
        """Загружаем TXT-шаблон"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(self.url) as response:
                    if response.status == 200:
                        data = await response.text()
                        return [line.strip() for line in data.splitlines() if line.strip()]
                    else:
                        return None
        except Exception as e:
            return str(e)

    # 🔹 Главный спам-цикл
    @loader.command()
    async def sex(self, message):
        """Запустить еблю (онлайн-спам)"""
        if self.spam_active:
            return await utils.answer(message, self.strings["already_running"])

        phrases = await self.get_messages()
        if not phrases or isinstance(phrases, str):
            return await utils.answer(message, self.strings["error_no_messages"])

        self.spam_active = True
        await utils.answer(message, self.strings["spam_started"])

        try:
            while self.spam_active:
                await message.client.send_message(message.chat_id, random.choice(phrases))
                await asyncio.sleep(random.uniform(0.08, 0.5))
        except errors.FloodWaitError as e:
            await asyncio.sleep(e.seconds)
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

    # 🔹 Ставим авто-байтинг
    @loader.command()
    async def q(self, message):
        """Ответом на сообщение — включить байтинг на пользователя"""
        if not message.is_reply:
            return await utils.answer(message, self.strings["q_no_reply"])

        reply_msg = await message.get_reply_message()
        target_id = reply_msg.sender_id
        chat_id = message.chat_id

        self.q_targets.setdefault(chat_id, set()).add(target_id)

        # Мгновенно удаляем команду
        await message.delete()

        user_name = utils.get_display_name(reply_msg.sender)
        # Сообщение о добавлении можно опустить, но вставлю для логов в консоль
        await utils.answer(reply_msg, self.strings["q_added"].format(user_name))

    # 🔹 Очищаем все цели
    @loader.command()
    async def qq(self, message):
        """Сбросить все байты"""
        self.q_targets.clear()
        await utils.answer(message, self.strings["qq_done"])

    # 🔹 Выводим список
    @loader.command()
    async def qwe(self, message):
        """Вывести список активных байтингов"""
        if not self.q_targets:
            return await utils.answer(message, "❌ <b>Нет активных байтов</b>")

        out = self.strings["qwe_header"]
        for chat_id, users in self.q_targets.items():
            try:
                chat_title = (await message.client.get_entity(chat_id)).title
            except:
                chat_title = str(chat_id)
            out += f"\n<b>{chat_title}</b>:\n"
            for uid in users:
                try:
                    name = utils.get_display_name(await message.client.get_entity(uid))
                except:
                    name = str(uid)
                out += f"  ╰ 💬 {name}\n"
        await utils.answer(message, out)

    # 🔹 Слежка за сообщениями
    async def watcher(self, message):
        if not getattr(message, "sender_id", None):
            return
        chat_id = message.chat_id
        user_id = message.sender_id

        if chat_id in self.q_targets and user_id in self.q_targets[chat_id]:
            phrases = await self.get_messages()
            if not phrases or isinstance(phrases, str):
                return
            try:
                await message.reply(random.choice(phrases))
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
                await message.reply(random.choice(phrases))
