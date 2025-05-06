import logging
from aiogram import Bot, Dispatcher, types
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command
import random
import time
from datetime import datetime, timedelta
import asyncio
import re
import matplotlib.pyplot as plt
import io
import aiohttp
from collections import defaultdict

# Cooldowns
message_cooldowns = defaultdict(float)
action_cooldowns = defaultdict(lambda: defaultdict(float))
MESSAGE_COOLDOWN = 2.5
ACTION_COOLDOWN = 3600  # 60 minutes
BOOBS_COOLDOWN = 3600  # 60 minutes

logging.basicConfig(level=logging.INFO)

API_TOKEN = '7632023422:AAFvrAScl0hO_Cq0bbvMWeMUJKuxjuWUSME'
storage = MemoryStorage()
dp = Dispatcher(bot=bot, storage=storage)

users_db = {}
chat_states = {}
warns = {}
admins = {1336991712}  # Добавляем ID администратора
marriages = {}
clans = {}
achievements = {}
user_inventory = {}
pets = {}
nsfw_actions = {}
user_languages = {}  # Словарь для хранения языковых настроек
user_rewards = {}  # Словарь для хранения наград пользователей
weather_api_key = "d9ca78488c57662e41f7a674e3af55cf"  # OpenWeatherMap API key

DEFAULT_LANG = 'ru'

async def get_weather(city):
    try:
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={weather_api_key}&units=metric&lang=ru"
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                data = await response.json()
                if str(data.get("cod", "")) != "200":
                    return "Город не найден"

                weather = {
                    'temp': round(data['main']['temp']),
                    'feels_like': round(data['main']['feels_like']),
                    'humidity': data['main']['humidity'],
                    'wind_speed': data['wind']['speed'],
                    'description': data['weather'][0]['description'],
                }

                return f"""🌡 Погода {city}

☁️ Сейчас: +{weather['temp']}° | {weather['description']}
🧖‍♂️ Ощущается как: +{weather['feels_like']}°
↖️ Ветер: {weather['wind_speed']} м/с
💦 Влажность: {weather['humidity']}%"""
    except Exception as e:
        return "Ошибка при получении погоды"

def get_text(key, lang):
    texts = {
        'stats': {
            'ru': "📊 Статистика {}:\n",
            'en': "📊 Statistics for {}:\n"
        },
        'messages': {
            'ru': "Сообщений: {}\n",
            'en': "Messages: {}\n"
        },
        'karma': {
            'ru': "Карма: {}\n",
            'en': "Karma: {}\n"
        },
        'dick': {
            'ru': "Размер члена: {}см\n",
            'en': "Dick size: {}cm\n"
        },
        'boobs': {
            'ru': "Размер груди: {}\n",
            'en': "Boobs size: {}\n"
        }
    }
    return texts.get(key, {}).get(lang, texts[key]['ru'])

async def generate_stats_image(user_data):
    plt.clf()
    plt.style.use('dark_background')
    fig = plt.figure(figsize=(10, 6))
    plt.rcParams['figure.facecolor'] = '#36393F'
    plt.rcParams['axes.facecolor'] = '#2F3136'

    # Create main graph
    plt.subplot(2, 2, 1)
    plt.bar(['Messages'], [user_data['messages']], color='#00ff00')
    plt.title('Messages')

    # Create karma graph
    plt.subplot(2, 2, 2)
    plt.bar(['Karma'], [user_data['karma']], color='#ff00ff')
    plt.title('Karma')

    # Create level progress
    plt.subplot(2, 2, 3)
    plt.pie([user_data['exp'], 100-user_data['exp']], 
            colors=['#00ff00', '#333333'],
            labels=[f'{user_data["exp"]}%', ''],
            autopct='%1.1f%%')
    plt.title(f'Level {user_data["level"]} Progress')

    # Create additional stats
    plt.subplot(2, 2, 4)
    stats = [user_data.get('dick_size', 0), user_data.get('boobs_size', 0)]
    plt.bar(['🍆', '🍈'], stats, color=['#ff0000', '#ff69b4'])
    plt.title('Body Stats')

    plt.tight_layout()
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor='#36393F')
    buf.seek(0)
    return buf

@dp.message(Command('start', 'menu', 'меню'))
async def start_command(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="📊 Профиль", callback_data="profile"),
            types.InlineKeyboardButton(text="📈 Статистика", callback_data="stats")
        ],
        [
            types.InlineKeyboardButton(text="🎲 Действия", callback_data="actions"),
            types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
        ]
    ])
    await message.reply("👊 Выберите действие:", reply_markup=keyboard)

@dp.callback_query()
async def callback_handler(callback: types.CallbackQuery):
    if callback.data == "profile":
        await profile(callback.message)
    elif callback.data == "stats":
        await show_stats(callback.message)
    elif callback.data == "actions":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🍆 Дрочить", callback_data="dick"),
                types.InlineKeyboardButton(text="🍈 Жмякать", callback_data="boobs")
            ],
            [
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
            ]
        ])
        await callback.message.edit_text("Выберите действие:", reply_markup=keyboard)
    elif callback.data == "settings":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🇷🇺 RU", callback_data="lang_ru"),
                types.InlineKeyboardButton(text="🇬🇧 EN", callback_data="lang_en")
            ],
            [
                types.InlineKeyboardButton(text="🔙 Назад", callback_data="menu")
            ]
        ])
        await callback.message.edit_text("⚙️ Выберите язык:", reply_markup=keyboard)
    elif callback.data == "menu":
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="📊 Профиль", callback_data="profile"),
                types.InlineKeyboardButton(text="📈 Статистика", callback_data="stats")
            ],
            [
                types.InlineKeyboardButton(text="🎲 Действия", callback_data="actions"),
                types.InlineKeyboardButton(text="⚙️ Настройки", callback_data="settings")
            ]
        ])
        await callback.message.edit_text("👊 Выберите действие:", reply_markup=keyboard)
    elif callback.data.startswith("lang_"):
        lang = callback.data.split("_")[1]
        user_languages[callback.from_user.id] = lang
        await callback.answer(f"✅ Язык изменен на: {lang.upper()}")
        await callback.message.edit_text("✅ Язык успешно изменен!")
    elif callback.data in ["dick", "boobs"]:
        if callback.data == "dick":
            await grow_dick(callback.message)
        else:
            await grow_boobs(callback.message)
    await callback.answer()

@dp.message(Command('help'))
async def help_command(message: types.Message):
    help_text = """
💫 Основные команды:
/profile - твой профиль со статистикой
/top - топ пользователей
/marry - пожениться
/clan - управление кланом
/pet - питомец
/shop - магазин
/inventory - инвентарь
/achievements - достижения
/roll - бросить кости
/say - сказать от имени бота
/me - действие от первого лица
/report - пожаловаться на пользователя

🔞 NSFW команды:
/otlizat - отлизать
/fuck - выебать
/kiss - поцеловать
/hug - обнять

👑 Админские команды:
/ban - забанить
/unban - разбанить
/warn - выдать предупреждение
/unwarn - снять предупреждение
/mute - замутить
/unmute - размутить
/kick - кикнуть
"""
    await message.reply(help_text)

@dp.message(lambda msg: msg.text and msg.text.lower().startswith('наградить'))
async def reward_user(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя, которого хотите наградить")

    reward_text = message.text[9:].strip()  # Remove "наградить" from the start
    if not reward_text:
        return await message.reply("Укажите текст награды")

    user_id = message.reply_to_message.from_user.id
    if user_id not in user_rewards:
        user_rewards[user_id] = []

    user_rewards[user_id].append(reward_text)
    await message.reply(f"✨ Награда '{reward_text}' выдана!")

@dp.message(lambda msg: msg.text and msg.text.lower().startswith('погода'))
async def weather_command(message: types.Message):
    city = message.text[7:].strip()  # Remove "погода " from the start
    if not city:
        return await message.reply("Укажите город")

    weather_text = await get_weather(city)
    await message.reply(weather_text)

@dp.message(Command('profile'))
async def profile(message: types.Message):
    user_id = message.from_user.id
    if user_id not in users_db:
        users_db[user_id] = {
            'messages': 0,
            'karma': 0,
            'coins': 0,
            'level': 1,
            'exp': 0,
            'married_to': None,
            'clan': None,
            'achievements': []
        }

    user = users_db[user_id]
    text = f"👤 Профиль {message.from_user.first_name}:\n"
    text += f"💬 Сообщений: {user['messages']}\n"
    text += f"💰 Монет: {user['coins']}\n"
    text += f"📊 Уровень: {user['level']}\n"
    text += f"⭐️ Опыт: {user['exp']}/100\n"
    text += f"💕 Брак: {user['married_to'] or 'Свободен(а)'}\n"
    text += f"👥 Клан: {user['clan'] or 'Нет'}\n"

    # Add rewards
    if message.from_user.id in user_rewards and user_rewards[message.from_user.id]:
        text += "\n🏆 Награды:\n"
        for reward in user_rewards[message.from_user.id]:
            text += f"• {reward}\n"

    stats_image = await generate_stats_image(user)
    await message.reply_photo(photo=types.BufferedInputFile(stats_image.getvalue(), filename="profile.png"), caption=text)

@dp.message(Command(commands=['otlizat', 'fuck', 'kiss', 'hug']))
async def nsfw_action(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение того, с кем хочешь взаимодействовать!")

    action = message.text.split('@')[0][1:]
    actions = {
        'otlizat': 'отлизал(а) 👅',
        'fuck': 'выебал(а) 🍆',
        'kiss': 'поцеловал(а) 💋',
        'hug': 'обнял(а) 🤗'
    }

    user1 = message.from_user.first_name
    user2 = message.reply_to_message.from_user.first_name

    await message.reply(f"💕 {user1} {actions[action]} {user2}")

@dp.message(Command('marry'))
async def marry(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответь на сообщение того, кому хочешь сделать предложение!")

    user1_id = message.from_user.id
    user2_id = message.reply_to_message.from_user.id

    if user1_id == user2_id:
        return await message.reply("Нельзя жениться на себе!")

    if user1_id in marriages or user2_id in marriages:
        return await message.reply("Кто-то уже в браке!")

    marriages[user1_id] = user2_id
    marriages[user2_id] = user1_id

    users_db[user1_id]['married_to'] = message.reply_to_message.from_user.first_name
    users_db[user2_id]['married_to'] = message.from_user.first_name

    await message.reply(f"💕 {message.from_user.first_name} и {message.reply_to_message.from_user.first_name} теперь в браке!")

@dp.message(Command('clan'))
async def clan(message: types.Message):
    user_id = message.from_user.id
    args = message.text.split()

    if len(args) == 1:
        return await message.reply("""
🛡 Команды клана:
/clan create [название] - создать клан
/clan info - информация о клане
/clan join [название] - вступить в клан
/clan leave - покинуть клан
""")

    action = args[1]

    if action == "create" and len(args) > 2:
        clan_name = args[2]
        if clan_name in clans:
            return await message.reply("Такой клан уже существует!")

        clans[clan_name] = {
            'leader': user_id,
            'members': [user_id],
            'level': 1,
            'exp': 0
        }
        users_db[user_id]['clan'] = clan_name
        await message.reply(f"🛡 Клан {clan_name} создан!")

@dp.message(Command('pet'))
async def pet(message: types.Message):
    user_id = message.from_user.id
    if user_id not in pets:
        pets[user_id] = {
            'name': None,
            'type': None,
            'level': 1,
            'hunger': 100,
            'happiness': 100
        }

    pet = pets[user_id]
    if not pet['name']:
        return await message.reply("""
🐾 У тебя нет питомца! Выбери питомца:
/pet buy cat - купить кота
/pet buy dog - купить собаку
/pet buy hamster - купить хомяка
""")

    text = f"🐾 Твой питомец {pet['name']}:\n"
    text += f"Тип: {pet['type']}\n"
    text += f"Уровень: {pet['level']}\n"
    text += f"Голод: {pet['hunger']}/100\n"
    text += f"Счастье: {pet['happiness']}/100"

    await message.reply(text)

@dp.message(Command('roll'))
async def roll(message: types.Message):
    number = random.randint(1, 100)
    await message.reply(f"🎲 {message.from_user.first_name} выбросил(а): {number}")

@dp.message(Command('say'))
async def say(message: types.Message):
    text = message.text.replace('/say ', '', 1)
    if text:
        await message.delete()
        await message.answer(text)

async def check_cooldown(user_id: int, action: str = None) -> bool:
    current_time = time.time()

    if action:
        last_action = action_cooldowns[user_id][action]
        if current_time - last_action < ACTION_COOLDOWN:
            minutes_left = int((ACTION_COOLDOWN - (current_time - last_action)) / 60)
            return False, f"⏳ Подождите {minutes_left} минут"
        action_cooldowns[user_id][action] = current_time
    else:
        last_message = message_cooldowns[user_id]
        if current_time - last_message < MESSAGE_COOLDOWN:
            return False, "🚫 Не спамьте"
        message_cooldowns[user_id] = current_time

    return True, None

@dp.message(Command("команды", "commands", "help", "помощь"))
@dp.message(Command("langhuy"))
async def set_language(message: types.Message):
    try:
        lang = message.text.split()[1].lower()
        if lang not in ['ru', 'en']:
            await message.reply("❌ Supported languages: ru, en")
            return

        user_languages[message.from_user.id] = lang
        await message.reply(f"✅ Language set to: {lang.upper()}")
    except:
        await message.reply("❌ Usage: /langhuy [ru/en]")

async def commands_list(message: types.Message):
    text = """
📋 Команды бота:

👤 Профиль:
стат, статистика - показать статистику
дроч - увеличить размер
жмяк - увеличить грудь
топ хуев - топ по размеру

💬 Общение:
/me <действие> - действие от первого лица
/say <текст> - сказать от имени бота

💕 Отношения:
/marry - пожениться
/kiss - поцеловать
/hug - обнять

🎮 Развлечения:
/roll - бросить кости
/pet - питомец
/clan - клан

🛡 Модерация:
/warn - выдать предупреждение
/unwarn - снять предупреждение
/ban - забанить
/unban - разбанить
"""
    msg = await message.reply(text)
    await asyncio.sleep(30)
    await msg.delete()

@dp.message(lambda msg: msg.text and msg.text.lower() in ['стат', 'статистика', 'стата', 'stat', 'stats'])
async def show_stats(message: types.Message):
    user_id = message.from_user.id
    chat_id = message.chat.id

    try:
        if user_id not in users_db:
            users_db[user_id] = {
                'messages': 0,
                'warns': 0,
                'karma': 0,
                'dick_size': random.randint(1, 30),
                'boobs_size': random.randint(1, 5),
                'level': 1,
                'exp': 0,
                'coins': 0
            }

        stats = users_db[user_id]
        
        # Create stats image
        plt.clf()
        plt.style.use('dark_background')
        fig = plt.figure(figsize=(10, 6))
        
        # User info at the top
        plt.suptitle(f"Статистика {message.from_user.first_name}", fontsize=16)
        plt.figtext(0.02, 0.98, f"Уровень: {stats['level']}", fontsize=12)
        plt.figtext(0.3, 0.98, f"Сообщений: {stats['messages']}", fontsize=12)
        
        # Main stats
        plt.subplot(2, 2, 1)
        plt.bar(['Опыт'], [stats['exp']], color='#00ff00')
        plt.title('Опыт до след. уровня')
        
        plt.subplot(2, 2, 2)
        plt.bar(['Карма'], [stats['karma']], color='#ff00ff')
        plt.title('Карма')
        
        plt.subplot(2, 2, 3)
        plt.bar(['🍆'], [stats['dick_size']], color='#ff0000')
        plt.title('Размер')
        
        plt.subplot(2, 2, 4)
        plt.bar(['🍈'], [stats['boobs_size']], color='#ff69b4')
        plt.title('Грудь')
        
        plt.tight_layout()
        buf = io.BytesIO()
        plt.savefig(buf, format='png', facecolor='#36393F', bbox_inches='tight')
        buf.seek(0)
        
        # Get user's position in top
        msg_top = sorted(users_db.items(), key=lambda x: x[1].get('messages', 0), reverse=True)
        position = next(i for i, (uid, _) in enumerate(msg_top, 1) if uid == user_id)
        
        text = f"📊 Статистика {message.from_user.first_name}\n"
        text += f"👑 Место в топе: #{position}\n"
        text += f"📨 Сообщений: {stats['messages']}\n"
        text += f"⭐️ Уровень: {stats['level']}\n"
        text += f"💫 Опыт: {stats['exp']}/100"
        
        await message.reply_photo(photo=types.BufferedInputFile(buf.getvalue(), filename="stats.png"), caption=text)
    except Exception as e:
        await message.answer("❌ Произошла ошибка")

# Duel system
duel_stats = {}
aim_stats = {}

@dp.message(lambda msg: msg.text and msg.text.lower() in ['топ', 'top'])
async def show_top(message: types.Message):
    try:
        # Sort by messages
        msg_top = sorted(users_db.items(), key=lambda x: x[1].get('messages', 0), reverse=True)[:5]
        # Sort by dick size
        dick_top = sorted(users_db.items(), key=lambda x: x[1].get('dick_size', 0), reverse=True)[:5]
        # Sort by duel wins
        duel_top = sorted(duel_stats.items(), key=lambda x: x[1].get('wins', 0), reverse=True)[:5]

        text = "📊 Топ пользователей:\n\n"
        text += "💬 По сообщениям:\n"
        for i, (user_id, stats) in enumerate(msg_top, 1):
            try:
                user = await bot.get_chat_member(message.chat.id, user_id)
                text += f"{i}. {user.user.first_name}: {stats.get('messages', 0)}\n"
            except: continue

        text += "\n🍆 По размеру:\n"
        for i, (user_id, stats) in enumerate(dick_top, 1):
            try:
                user = await bot.get_chat_member(message.chat.id, user_id)
                text += f"{i}. {user.user.first_name}: {stats.get('dick_size', 0)}см\n"
            except: continue

        text += "\n🎯 По дуэлям:\n"
        for i, (user_id, stats) in enumerate(duel_top, 1):
            try:
                user = await bot.get_chat_member(message.chat.id, user_id)
                text += f"{i}. {user.user.first_name}: {stats.get('wins', 0)} побед\n"
            except: continue

        await message.answer(text)
    except Exception as e:
        await message.answer("❌ Произошла ошибка")

@dp.message(Command("дуэль", "duel"))
async def duel_command(message: types.Message):
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение того, кого вызываете на дуэль!")

    user1_id = message.from_user.id
    user2_id = message.reply_to_message.from_user.id

    if user1_id == user2_id:
        return await message.reply("Нельзя вызвать на дуэль самого себя!")

    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
        [
            types.InlineKeyboardButton(text="✅ Принять", callback_data=f"duel_accept_{user1_id}"),
            types.InlineKeyboardButton(text="❌ Отказаться", callback_data=f"duel_decline_{user1_id}")
        ]
    ])
    
    await message.reply(
        f"🎯 {message.reply_to_message.from_user.first_name}, вас вызвали на дуэль!",
        reply_markup=keyboard
    )

@dp.callback_query(lambda c: c.data.startswith('duel_'))
async def duel_callback(callback: types.CallbackQuery):
    action, user1_id = callback.data.split('_')[1:]
    user1_id = int(user1_id)
    user2_id = callback.from_user.id

    if action == "decline":
        await callback.message.edit_text("🏳️ Дуэль отклонена!")
        return

    if action == "accept":
        # Initialize aim bonus
        aim_stats[user1_id] = 0
        aim_stats[user2_id] = 0

        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [
                types.InlineKeyboardButton(text="🎯 Прицелиться", callback_data=f"aim_{user1_id}_{user2_id}"),
                types.InlineKeyboardButton(text="🔫 Стрелять", callback_data=f"shoot_{user1_id}_{user2_id}")
            ],
            [
                types.InlineKeyboardButton(text="💨 Сбить прицел", callback_data=f"disturb_{user1_id}_{user2_id}")
            ]
        ])
        
        await callback.message.edit_text(
            "🎯 Дуэль началась!\nПрицельтесь для повышения точности или стреляйте!",
            reply_markup=keyboard
        )

@dp.callback_query(lambda c: c.data.startswith(('aim_', 'shoot_', 'disturb_')))
async def duel_action(callback: types.CallbackQuery):
    action, user1_id, user2_id = callback.data.split('_')
    user1_id = int(user1_id)
    user2_id = int(user2_id)
    current_user = callback.from_user.id

    if current_user not in [user1_id, user2_id]:
        await callback.answer("Вы не участвуете в этой дуэли!")
        return

    if action == "aim":
        aim_stats[current_user] = min(aim_stats.get(current_user, 0) + 3, 30)  # Max 30% bonus
        await callback.answer(f"Точность повышена на 3%! Текущий бонус: {aim_stats[current_user]}%")
        return

    if action == "disturb":
        opponent = user2_id if current_user == user1_id else user1_id
        if aim_stats.get(opponent, 0) > 0:
            aim_stats[opponent] = max(0, aim_stats[opponent] - 5)
            await callback.answer(f"Вы сбили прицел противника! Его бонус: {aim_stats[opponent]}%")
        else:
            await callback.answer("У противника нет бонуса прицеливания!")
        return

    if action == "shoot":
        shooter = current_user
        target = user2_id if shooter == user1_id else user1_id
        
        base_chance = 50
        aim_bonus = aim_stats.get(shooter, 0)
        hit_chance = min(95, base_chance + aim_bonus)  # Max 95% chance
        
        if random.randint(1, 100) <= hit_chance:
            # Update stats
            if shooter not in duel_stats:
                duel_stats[shooter] = {'wins': 0, 'losses': 0}
            if target not in duel_stats:
                duel_stats[target] = {'wins': 0, 'losses': 0}
            
            duel_stats[shooter]['wins'] = duel_stats[shooter].get('wins', 0) + 1
            duel_stats[target]['losses'] = duel_stats[target].get('losses', 0) + 1

            shooter_name = callback.from_user.first_name
            await callback.message.edit_text(f"💥 {shooter_name} побеждает в дуэли!")
        else:
            await callback.message.edit_text("💨 Промах! Дуэль окончена!")

        # Reset aim stats
        aim_stats[user1_id] = 0
        aim_stats[user2_id] = 0

@dp.message(lambda msg: msg.text and msg.text.lower() in ['дроч', 'подрочить', 'fap', 'masturbate'])
async def grow_dick(message: types.Message):
    user_id = message.from_user.id

    try:
        # Check cooldown
        can_proceed, error_msg = await check_cooldown(user_id, 'dick')
        if not can_proceed:
            msg = await message.reply(error_msg)
            await asyncio.sleep(2)
            await msg.delete()
            return

        if user_id not in users_db:
            users_db[user_id] = {'dick_size': random.randint(1, 30)}

        growth = random.randint(-2, 5)
        users_db[user_id]['dick_size'] = max(1, users_db[user_id].get('dick_size', 1) + growth)

        if growth > 0:
            await message.answer(f"🍆 +{growth}см! Теперь/Now: {users_db[user_id]['dick_size']}см")
        else:
            await message.answer(f"😢 {growth}см! Теперь/Now: {users_db[user_id]['dick_size']}см")
    except Exception as e:
        await message.answer("❌ Произошла ошибка/Error occurred")

@dp.message(lambda msg: msg.text and msg.text.lower() in ['жмяк', 'массаж', 'squeeze', 'massage'])
async def grow_boobs(message: types.Message):
    user_id = message.from_user.id

    try:
        # Check cooldown
        can_proceed, error_msg = await check_cooldown(user_id, 'boobs')
        if not can_proceed:
            msg = await message.reply(error_msg)
            await asyncio.sleep(2)
            await msg.delete()
            return

        if user_id not in users_db:
            users_db[user_id] = {'boobs_size': random.randint(1, 5)}

        growth = random.randint(-1, 2)
        users_db[user_id]['boobs_size'] = max(1, users_db[user_id].get('boobs_size', 1) + growth)

        size_str = "🍈" * users_db[user_id]['boobs_size']
        msg = await message.reply(f"{'💗 +' if growth > 0 else '😢 '}{growth}! Теперь: {size_str}")
        await asyncio.sleep(5)
        await msg.delete()
    except Exception as e:
        msg = await message.reply("❌ Ошибка")
        await asyncio.sleep(2)
        await msg.delete()

@dp.message()
async def handle_messages(message: types.Message):
    if message.text is None:
        return
    user_id = message.from_user.id

    # Check cooldown
    can_proceed, error_msg = await check_cooldown(user_id)
    if not can_proceed:
        msg = await message.reply(error_msg)
        await asyncio.sleep(2)
        await msg.delete()
        return

    try:
        if user_id not in users_db:
            users_db[user_id] = {
                'messages': 0,
                'warns': 0,
                'karma': 0,
                'coins': 0,
                'level': 1,
                'exp': 0,
                'dick_size': random.randint(1, 30),
                'boobs_size': random.randint(1, 5)
            }

        users_db[user_id]['messages'] = users_db[user_id].get('messages', 0) + 1
        users_db[user_id]['exp'] = users_db[user_id].get('exp', 0) + random.randint(1, 5)
    except Exception as e:
        print(f"Error in handle_messages: {e}")

    if users_db[user_id]['exp'] >= 100:
        users_db[user_id]['level'] += 1
        users_db[user_id]['exp'] = 0
        achievement = f"🎉 Достигнут {users_db[user_id]['level']} уровень!"
        if achievement not in users_db[user_id].get('achievements', []):
            users_db[user_id].setdefault('achievements', []).append(achievement)
        await message.reply(f"🎉 {message.from_user.first_name} достиг {users_db[user_id]['level']} уровня!")

    if random.random() < 0.1:
        coins = random.randint(1, 10)
        users_db[user_id]['coins'] += coins
        await message.reply(f"💰 +{coins} монет!")

async def is_admin(user_id: int, chat_id: int) -> bool:
    if chat_id not in admins:
        chat_admins = await bot.get_chat_administrators(chat_id)
        admins[chat_id] = [admin.user.id for admin in chat_admins]
    return user_id in admins[chat_id]

@dp.message(Command(commands=['ban', 'бан']))
async def ban_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")
        
    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя, которого хотите забанить!")

    try:
        await message.chat.ban(message.reply_to_message.from_user.id)
        await message.reply(f"🔨 Пользователь {message.reply_to_message.from_user.first_name} забанен!")
    except Exception as e:
        await message.reply("❌ Не удалось забанить пользователя!")

@dp.message(Command(commands=['unban', 'разбан']))
async def unban_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")

    try:
        user_id = int(message.text.split()[1])
        await message.chat.unban(user_id)
        await message.reply("✅ Пользователь разбанен!")
    except:
        await message.reply("❌ Укажите корректный ID пользователя!")

@dp.message(Command(commands=['mute', 'мут']))
async def mute_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")

    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя!")

    try:
        duration = int(message.text.split()[1]) * 60  # minutes to seconds
        until_date = datetime.now() + timedelta(seconds=duration)
        await message.chat.restrict(
            message.reply_to_message.from_user.id,
            permissions=types.ChatPermissions(can_send_messages=False),
            until_date=until_date
        )
        await message.reply(f"🤐 Пользователь {message.reply_to_message.from_user.first_name} замучен на {duration//60} минут!")
    except:
        await message.reply("❌ Укажите время мута в минутах!")

@dp.message(Command(commands=['unmute', 'размут']))
async def unmute_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")

    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя!")

    try:
        await message.chat.restrict(
            message.reply_to_message.from_user.id,
            permissions=types.ChatPermissions(can_send_messages=True)
        )
        await message.reply(f"✅ Пользователь {message.reply_to_message.from_user.first_name} размучен!")
    except:
        await message.reply("❌ Не удалось размутить пользователя!")

@dp.message(Command(commands=['warn', 'варн']))
async def warn_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")

    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя!")

    user_id = message.reply_to_message.from_user.id
    if user_id not in warns:
        warns[user_id] = 0
    warns[user_id] += 1

    if warns[user_id] >= 3:
        try:
            await message.chat.ban(user_id)
            await message.reply(f"🔨 Пользователь {message.reply_to_message.from_user.first_name} забанен за превышение предупреждений!")
            warns[user_id] = 0
        except:
            await message.reply("❌ Не удалось забанить пользователя!")
    else:
        await message.reply(f"⚠️ Пользователь {message.reply_to_message.from_user.first_name} получил предупреждение! ({warns[user_id]}/3)")

@dp.message(Command(commands=['unwarn', 'унварн']))
async def unwarn_user(message: types.Message):
    if not await is_admin(message.from_user.id, message.chat.id):
        return await message.reply("❌ У вас нет прав администратора!")

    if not message.reply_to_message:
        return await message.reply("Ответьте на сообщение пользователя!")

    user_id = message.reply_to_message.from_user.id
    if user_id in warns and warns[user_id] > 0:
        warns[user_id] -= 1
        await message.reply(f"✅ С пользователя {message.reply_to_message.from_user.first_name} снято предупреждение! ({warns[user_id]}/3)")
    else:
        await message.reply("У пользователя нет предупреждений!")

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
