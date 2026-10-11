from telethon import TelegramClient
import asyncio
import random
import os

# Данные Telegram API
API_ID = 37023215
API_HASH = "aa0a77b3d7a4694503b473a22c60f126"

# Telegram-клиент
client = TelegramClient("session", API_ID, API_HASH)

# Куда отправлять уведомления
ADMIN_CHAT = "@protokol159"

# Папки
MATERIALS_FOLDER = "Материалы"
PHOTOS_FOLDER = os.path.join(MATERIALS_FOLDER, "photos")

# Поддерживаемые форматы
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".webp")

# 3 недели + 2 дня
CYCLE_SLEEP = 23 * 24 * 60 * 60


async def notify(text):
    # Отправляем уведомление в Telegram
    try:
        await client.send_message(ADMIN_CHAT, text)
    except Exception as error:
        print(f"Ошибка уведомления: {error}")


async def send_messages():
    # Загружаем чаты
    with open(
        os.path.join(MATERIALS_FOLDER, "chats.txt"),
        "r",
        encoding="utf-8"
    ) as file:
        chats = [line.strip() for line in file if line.strip()]

    # Загружаем текст объявления
    with open(
        os.path.join(MATERIALS_FOLDER, "message.txt"),
        "r",
        encoding="utf-8"
    ) as file:
        message = file.read()

    # Ищем фотографии
    photos = [
        os.path.join(PHOTOS_FOLDER, file)
        for file in os.listdir(PHOTOS_FOLDER)
        if file.lower().endswith(SUPPORTED_FORMATS)
    ]

    photos.sort()

    # Проверяем фотографии
    if len(photos) < 3:
        text = (
            "⚠️ РАССЫЛКА НЕ ЗАПУЩЕНА\n\n"
            f"Найдено фото: {len(photos)}\n"
            "Нужно минимум: 3"
        )

        print(text)
        await notify(text)
        return

    # Используем первые 3 фотографии
    photos = photos[:3]

    success = 0
    errors = []

    # Начало рассылки
    start_text = (
        "🚀 РАССЫЛКА ЗАПУЩЕНА\n\n"
        f"Чатов: {len(chats)}\n"
        "Фото: 3\n"
        "Первое сообщение: сразу"
    )

    print("\n" + "=" * 40)
    print(start_text)
    print("=" * 40)

    await notify(start_text)

    # Рассылка
    for i, chat in enumerate(chats, start=1):

        # Первое сообщение отправляем сразу
        if i == 1:
            print(f"\n[{i}/{len(chats)}] Отправка сразу...")

        # Перед следующими сообщениями ждём случайный интервал
        else:
            delay = random.randint(3600, 10800)

            hours = delay // 3600
            minutes = (delay % 3600) // 60

            print(
                f"\n[{i}/{len(chats)}] "
                f"Ожидание: {hours} ч. {minutes} мин."
            )

            await asyncio.sleep(delay)

        try:
            # Отправляем 3 фотографии + текст
            await client.send_file(
                chat,
                photos,
                caption=message
            )

            success += 1

            print(f"✓ ОТПРАВЛЕНО → {chat}")

            # Если это не последний чат — заранее выбираем
            # интервал до следующей отправки
            if i < len(chats):
                next_delay = random.randint(3600, 10800)

                next_hours = next_delay // 3600
                next_minutes = (next_delay % 3600) // 60

                notification = (
                    f"✅ Отправлено\n"
                    f"Чат: {chat}\n"
                    f"Прогресс: {i}/{len(chats)}\n\n"
                    f"⏱ Следующий чат: {chats[i]}\n"
                    f"Через: {next_hours} ч. {next_minutes} мин."
                )

                await notify(notification)

                # Ждём выбранное время
                await asyncio.sleep(next_delay)

            else:
                await notify(
                    f"✅ Отправлено\n"
                    f"Чат: {chat}\n"
                    f"Прогресс: {i}/{len(chats)}\n\n"
                    "🏁 Это был последний чат."
                )

        except Exception as error:
            errors.append(f"{chat}: {error}")

            print(f"✗ НЕ ОТПРАВЛЕНО → {chat}")
            print(f"Причина: {error}")

            # Даже при ошибке заранее планируем следующий чат
            if i < len(chats):
                next_delay = random.randint(3600, 10800)

                next_hours = next_delay // 3600
                next_minutes = (next_delay % 3600) // 60

                await notify(
                    f"❌ Не отправлено\n"
                    f"Чат: {chat}\n"
                    f"Прогресс: {i}/{len(chats)}\n"
                    f"Причина: {error}\n\n"
                    f"➡️ Следующий чат: {chats[i]}\n"
                    f"Через: {next_hours} ч. {next_minutes} мин."
                )

                # Ошибка не останавливает рассылку
                await asyncio.sleep(next_delay)

            else:
                await notify(
                    f"❌ Не отправлено\n"
                    f"Чат: {chat}\n"
                    f"Прогресс: {i}/{len(chats)}\n"
                    f"Причина: {error}\n\n"
                    "🏁 Это был последний чат."
                )

    # Итог
    result_text = (
        "🏁 РАССЫЛКА ЗАВЕРШЕНА\n\n"
        f"Всего: {len(chats)}\n"
        f"Успешно: {success}\n"
        f"Ошибок: {len(errors)}"
    )

    print("\n" + "=" * 40)
    print(result_text)
    print("=" * 40)

    await notify(result_text)


async def main():
    # Подключаемся к Telegram
    await client.start()

    await notify(
        "🟢 Скрипт запущен\n"
        "Telegram подключён."
    )

    # Постоянная работа
    while True:

        await send_messages()

        print("\n⏳ Следующий цикл через 23 дня.")

        await notify(
            "⏳ Цикл завершён\n"
            "Следующая рассылка через 23 дня."
        )

        await asyncio.sleep(CYCLE_SLEEP)


# Запуск
with client:
    client.loop.run_until_complete(main())