import telebot
import random
import datetime
import threading
from telebot import types

bot = telebot.TeleBot('6428337642:AAHGqm88cznR7FPYzsErZPa9LRe79TSvxCA')


win_streak = {}  
win_record = {}

tamagotchis = {}
user_states = {}
last_update_times = {}  # Словарь для хранения времени последнего обновления параметров

class Tamagotchi:
    def __init__(self, owner_id, pet_name):
        self.owner_id = owner_id
        self.pet_name = pet_name
        self.health = 100
        self.hunger = 100
        self.happiness = 100
        self.age = 0
        self.last_update_time = datetime.datetime.now()
        self.inventory = {"Еда": {}, "Лекарство": {}, "Игрушки": {}}
        self.balance = 1000  # Баланс леденцев
        self.job = None  # Атрибут для хранения работы тамагочи
        self.salary = 0  # Атрибут для хранения зарплаты
   

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.chat.id
    if user_id not in tamagotchis:
        user_states[user_id] = 'creating_tamagotchi'
        bot.reply_to(message, "Привет! 😄 Я твой верный спутник, твой собственный тамагочи! 🐾 Давай придумаем мне имя?")
        bot.register_next_step_handler(message, create_tamagotchi_name)
        tamagotchis[user_id] = Tamagotchi(user_id, "")  # Создание экземпляра Tamagotchi
        tamagotchis[user_id].start = True  # Установка флага начала игры
    else:
        user_states[user_id] = 'existing_tamagotchi'
        show_existing_tamagotchi_menu(message)


def show_existing_tamagotchi_menu(message):
    user_id = message.chat.id
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    yes_button = types.KeyboardButton("Да, удалить тамагочи")
    no_button = types.KeyboardButton("Нет, оставить")
    keyboard.add(yes_button, no_button)
    
    bot.send_message(user_id, "У вас уже есть тамагочи. Хотите удалить его?", reply_markup=keyboard)
    bot.register_next_step_handler(message, handle_existing_tamagotchi)

def handle_existing_tamagotchi(message):
    user_id = message.chat.id
    if message.text.lower() == "да, удалить тамагочи":
        del tamagotchis[user_id]
        bot.send_message(user_id, "Ваш тамагочи успешно удален. Теперь вы можете создать нового.")
        start(message)
    elif message.text.lower() == "нет, оставить":
        bot.send_message(user_id, "Отлично! Ваш текущий тамагочи остается с вами.")
        show_main_menu(user_id)
    else:
        bot.send_message(user_id, "Пожалуйста, выберите одну из предложенных кнопок.")

def create_tamagotchi_name(message):
    user_id = message.chat.id
    pet_name = message.text.strip()  # Удаляем пробелы с начала и конца названия
    if ' ' in pet_name:
        markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
        retry_button = types.KeyboardButton("Попробовать ввести заново")
        markup.add(retry_button)
        bot.reply_to(message, "Название питомца не должно содержать пробелов. Пожалуйста, выберите другое имя.", reply_markup=markup)
        bot.register_next_step_handler(message, create_tamagotchi_name_retry)
    else:
       tamagotchis[user_id] = Tamagotchi(user_id, pet_name)
       message_text = f"Отлично! Твой Тамагочи {pet_name} готов к приключениям! 🎉\nЕсли тебе понадобится помощь, просто введи /help 😊"
       bot.send_message(user_id, message_text)
       show_main_menu(user_id)


def create_tamagotchi_name_retry(message):
    bot.send_message(message.chat.id, "Пожалуйста, введите название питомца без пробелов.")
    bot.register_next_step_handler(message, create_tamagotchi_name)

@bot.message_handler(commands=['stats'])
def handle_stats(message):
    user_id = message.chat.id
    show_main_menu(user_id, command='/stats')

def show_main_menu(user_id):
    if user_id in tamagotchis: 
        tamagotchi = tamagotchis[user_id]
        menu_text = f"{tamagotchi.pet_name}:\n"
        menu_text += f"Здоровье: {tamagotchi.health}\n"
        menu_text += f"Еда: {tamagotchi.hunger}\n"
        menu_text += f"Счастье: {tamagotchi.happiness}\n"
        menu_text += f"Возраст: {tamagotchi.age} год(а)\n"
        menu_text += "Выбери действие:\n/play - Поиграть\n/feed - Кормить\n/heal - Лечить\n/help - Помощь\n"
        bot.send_message(user_id, menu_text, reply_markup=get_main_menu_keyboard())
    else:
        bot.send_message(user_id, "Для начала создайте тамагочи с помощью команды /start")

def get_main_menu_keyboard():
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    play_button = telebot.types.KeyboardButton('/play')
    feed_button = telebot.types.KeyboardButton('/feed')
    heal_button = telebot.types.KeyboardButton('/heal')
    help_button = telebot.types.KeyboardButton('/help')
    keyboard.add(play_button, feed_button, heal_button, help_button)
    return keyboard

# Добавление товаров и их цен в магазин
shop_items = {
    "Еда": {
        "items": {
            "Корм для кошек": {"price": 10, "effect": 20},  # Эффект: увеличение сытости на 20
            "Семена": {"price": 8, "effect": 15},
            "Мясо": {"price": 15, "effect": 25},
            "Овощи": {"price": 12, "effect": 18},
            "Молоко": {"price": 7, "effect": 12}
        }
    },
    "Лекарство": {
        "items": {
            "Антибиотик": {"price": 20, "effect": 30},  # Эффект: увеличение здоровья на 30
            "Витамины": {"price": 15, "effect": 25},
            "Бинт": {"price": 10, "effect": 18},
            "Аспирин": {"price": 8, "effect": 12},
            "Шприц": {"price": 12, "effect": 20}
        }
    },
    "Игрушки": {
        "items": {
            "Мячик": {"price": 5, "effect": 2},  # Эффект: увеличение счастья на 2
            "Плюшевая игрушка": {"price": 10, "effect": 5},
            "Кубики": {"price": 8, "effect": 3},
            "Машинка": {"price": 15, "effect": 6},
            "Кукла": {"price": 12, "effect": 4}
        }
    }
}

# Обработчик для команды "/balance"
@bot.message_handler(commands=['balance'])
def show_balance(message):
    user_id = message.chat.id
    tamagotchi = tamagotchis.get(user_id)
    if tamagotchi:
        bot.send_message(user_id, f"Ваш баланс леденцев: {tamagotchi.balance}")
    else:
        bot.send_message(user_id, "Сначала создайте тамагочи с помощью команды /start")

# Обработчик для команды "/job"
@bot.message_handler(commands=['job'])
def get_job(message):
    user_id = message.chat.id
    tamagotchi = tamagotchis[user_id]

    if not tamagotchi.job:  # Если у тамагочи нет работы
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for job_name, job_info in jobs.items():
            keyboard.add(types.KeyboardButton(job_name))
        cancel_button = types.KeyboardButton("Отмена")
        keyboard.add(cancel_button)

        bot.send_message(user_id, "Выберите, какую работу вы хотите получить:", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_get_job_choice)
    else:
        bot.send_message(user_id, "У вас уже есть работа. Выполните её или уволитесь, чтобы получить новую.")
        show_main_menu(user_id)

# Обработчик для выбора работы
def process_get_job_choice(message):
    user_id = message.chat.id
    choice = message.text
    tamagotchi = tamagotchis[user_id]

    if choice == "Отмена":
        show_main_menu(user_id)
    elif choice in jobs:
        job_info = jobs[choice]
        tamagotchi.job = choice
        tamagotchi.salary = job_info["salary"]
        tamagotchi.job_duration = job_info["duration"]
        tamagotchi.food_cost_per_minute = job_info["food_cost_per_minute"]
        tamagotchi.mood_cost_per_minute = job_info["mood_cost_per_minute"]

        # Запускаем таймер для работы
        threading.Timer(tamagotchi.job_duration * 60, finish_job, [user_id]).start()

        bot.send_message(user_id, f"Вы успешно получили работу: {choice}. Работа будет длиться {tamagotchi.job_duration} минут. Зарплата составляет {job_info['salary']} леденцев. Работа заберет {tamagotchi.food_cost_per_minute * tamagotchi.job_duration} единиц еды и {tamagotchi.mood_cost_per_minute * tamagotchi.job_duration} единиц настроения.")
        show_main_menu(user_id)
    else:
        bot.send_message(user_id, "Пожалуйста, выберите одну из предложенных работ.")
        get_job(message)

# Функция для завершения работы
def finish_job(user_id):
    tamagotchi = tamagotchis[user_id]

    # Добавляем зарплату к балансу
    tamagotchi.balance += tamagotchi.salary

    # Вычитаем расход еды и настроения за время работы
    tamagotchi.hunger -= tamagotchi.food_cost_per_minute * tamagotchi.job_duration
    tamagotchi.happiness -= tamagotchi.mood_cost_per_minute * tamagotchi.job_duration

    # Сбрасываем информацию о работе
    tamagotchi.job = None
    tamagotchi.salary = 0
    tamagotchi.job_duration = 0
    tamagotchi.food_cost_per_minute = 0
    tamagotchi.mood_cost_per_minute = 0

    bot.send_message(user_id, f"Вы успешно завершили работу и получили зарплату. Теперь вы можете выбрать новую работу.")
        
# Словарь с разными работами и их зарплатами
jobs = {
    "Уборщик": {"salary": 10, "duration": 5, "food_cost_per_minute": 1, "mood_cost_per_minute": 2},
    "Официант": {"salary": 15, "duration": 10, "food_cost_per_minute": 2, "mood_cost_per_minute": 3},
    "Разнорабочий": {"salary": 12, "duration": 15, "food_cost_per_minute": 3, "mood_cost_per_minute": 4},
    # Добавьте сюда другие работы и зарплаты
}

# Обработчик для команды "/shop"
@bot.message_handler(commands=['shop'])
def show_shop(message):
    user_id = message.chat.id
    tamagotchi = tamagotchis.get(user_id)
    if tamagotchi:
        keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
        for category_name, category_info in shop_items.items():
            keyboard.add(types.KeyboardButton(category_name))
        back_button = types.KeyboardButton("Назад")
        keyboard.add(back_button)

        bot.send_message(user_id, "Добро пожаловать в магазин!\nВыберите категорию товаров:", reply_markup=keyboard)
        bot.register_next_step_handler(message, process_shop_category_choice)
    else:
        bot.send_message(user_id, "Сначала создайте тамагочи с помощью команды /start")

# Обработчик для команды "/inventory"
@bot.message_handler(commands=['inventory'])
def show_inventory(message):
    user_id = message.chat.id
    tamagotchi = tamagotchis.get(user_id)

    if tamagotchi:
        inventory_text = "Инвентарь:\n"
        for category_name, items in tamagotchi.inventory.items():
            inventory_text += f"{category_name}:\n"
            if items:
                for item_name, count in items.items():
                    inventory_text += f"- {item_name} ({count} шт.)\n"
            else:
                inventory_text += "- Пусто\n"
            inventory_text += "\n"

        bot.send_message(user_id, inventory_text)
    else:
        bot.send_message(user_id, "Сначала создайте тамагочи с помощью команды /start")

# Обработчик для выбора категории товаров в магазине
def process_shop_category_choice(message):
    user_id = message.chat.id
    choice = message.text
    if choice == "Назад":
        show_main_menu(user_id)
    elif choice in shop_items:
        show_category_items(user_id, choice)
    else:
        bot.send_message(user_id, "Такой категории товаров нет в магазине.")
        show_shop(message)

# Отправить список товаров из выбранной категории
def show_category_items(user_id, category_name):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    category_info = shop_items[category_name]
    for item_name, item_info in category_info["items"].items():
        effect_info = f" (Увеличение сытости: +{item_info['effect']})" if category_name == "Еда" else \
                      f" (Увеличение счастья: +{item_info['effect']})" if category_name == "Игрушки" else \
                      f" (Увеличение здоровья: +{item_info['effect']})" if category_name == "Лекарство" else ""
        button_text = f"{item_name} - {item_info['price']} лед.{effect_info}"
        keyboard.add(types.KeyboardButton(button_text))
    back_button = types.KeyboardButton("Назад")
    keyboard.add(back_button)

    bot.send_message(user_id, f"Выберите товар из категории '{category_name}':", reply_markup=keyboard)
    bot.register_next_step_handler_by_chat_id(user_id, process_item_choice, category_name)

# Обработчик для выбора товара из категории
def process_item_choice(message, category_name):
    user_id = message.chat.id
    choice = message.text
    if choice == "Назад":
        show_shop(message)
    else:
        item_name = choice.split(" - ")[0]
        category_info = shop_items[category_name]
        if item_name in category_info["items"]:
            buy_item(user_id, item_name, category_name)
        else:
            bot.send_message(user_id, "Такого товара нет в данной категории.")
            show_category_items(user_id, category_name)


# Функция для покупки товара
def buy_item(user_id, item_name, category_name):
    tamagotchi = tamagotchis[user_id]
    category_info = shop_items[category_name]
    item_info = category_info["items"][item_name]

    if tamagotchi.balance >= item_info["price"]:
        tamagotchi.balance -= item_info["price"]

        inventory = tamagotchi.inventory.get(category_name, {})
        if item_name in inventory:
            inventory[item_name] += 1
        else:
            inventory[item_name] = 1
        tamagotchi.inventory[category_name] = inventory

        bot.send_message(user_id, f"Вы купили {item_name} за {item_info['price']} леденцев.\n"
                                  f"{tamagotchi.pet_name} доволен покупкой!")
        show_main_menu(user_id)
    else:
        bot.send_message(user_id, "У вас недостаточно леденцев.")
        show_main_menu(user_id)

# Обработчик для команды "/feed"
@bot.message_handler(commands=['feed'])
def feed_pet(message):
    user_id = message.chat.id
    tamagotchi = tamagotchis[user_id]
    inventory = tamagotchi.inventory.get("Еда", [])

    if not inventory:
        bot.send_message(user_id, f"У вас нет еды в инвентаре. Посетите магазин, чтобы купить немного еды.")
        return

    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    for item_name in inventory:
        keyboard.add(types.KeyboardButton(item_name))
    cancel_button = types.KeyboardButton("Отмена")
    keyboard.add(cancel_button)

    bot.send_message(user_id, "Выберите, чем вы хотите покормить своего тамагочи:", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_feed_choice)

# Обработчик для выбора еды для кормления
def process_feed_choice(message):
    user_id = message.chat.id
    choice = message.text
    tamagotchi = tamagotchis[user_id]
    inventory = tamagotchi.inventory.get("Еда", [])

    if choice == "Отмена":
        show_main_menu(user_id)
    elif choice in inventory:
        feed_food(user_id, choice)
    else:
        bot.send_message(user_id, "У вас нет такой еды в инвентаре.")
        show_main_menu(user_id)

# Функция для кормления
def feed_food(user_id, food_name):
    tamagotchi = tamagotchis[user_id]
    inventory = tamagotchi.inventory["Еда"]
    item_info = shop_items["Еда"]["items"][food_name]

    if tamagotchi.hunger < 100:  # Проверка, чтобы не покушать, если уже сыт
        if food_name in inventory:
            inventory[food_name] -= 1
            if inventory[food_name] == 0:
                del inventory[food_name]
            tamagotchi.inventory["Еда"] = inventory

            tamagotchi.hunger += item_info['effect']
            if tamagotchi.hunger > 100:
                tamagotchi.hunger = 100

            bot.send_message(user_id, f"{tamagotchi.pet_name} покушал {food_name} и теперь сыт.")
            show_main_menu(user_id)
        else:
            bot.send_message(user_id, "У вас нет такой еды в инвентаре.")
            show_main_menu(user_id)
    else:
        bot.send_message(user_id, f"{tamagotchi.pet_name} уже сыт и не хочет есть.")
        show_main_menu(user_id)



# Обработчик для кнопки "/heal"
@bot.message_handler(commands=['heal'])
def heal_pet(message):
    user_id = message.chat.id
    if user_id in tamagotchis:
        tamagotchi = tamagotchis[user_id]
        if tamagotchi.health < 100:
            tamagotchi.health = min(100, tamagotchi.health + 20)  # Увеличиваем здоровья
            bot.send_message(user_id, f"{tamagotchi.pet_name} почувствовал себя лучше!")
            show_main_menu(user_id)
        else:
            bot.send_message(user_id, "Питомец полностью здоров!")

@bot.message_handler(commands=['play'])
def play_with_tamagotchi(message):
    user_id = message.chat.id
    if user_id in tamagotchis:
        show_play_menu(user_id)

def show_play_menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    game1_button = telebot.types.KeyboardButton('Камень, ножницы, бумага')
    game2_button = telebot.types.KeyboardButton('Орёл и Решка')
    game3_button = telebot.types.KeyboardButton('Игра 3')
    back_button = telebot.types.KeyboardButton('Назад')
    keyboard.add(game1_button, game2_button, game3_button, back_button)
    bot.send_message(user_id, "Выберите игру:", reply_markup=keyboard)

@bot.message_handler(func=lambda message: message.text == 'Камень, ножницы, бумага' or message.text == 'Орёл и Решка' or message.text == 'Игра 3')
def handle_game_choice(message):
    user_id = message.chat.id
    if user_id in tamagotchis:
        game_choice = message.text
        if game_choice == 'Камень, ножницы, бумага':
            play_rock_paper_scissors(user_id)  # Вызываем функцию для игры "Камень, ножницы, бумага"
        elif game_choice == 'Орёл и Решка':
            play_heads_or_tails(user_id)
            pass
        elif game_choice == 'Игра 3':
            # Код для другой игры 3
            pass

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'end_game')
def handle_end_game(message):
    user_id = message.chat.id
    if message.text.lower() == "сыграть заново":
        if user_states[user_id] == 'playing_rock_paper_scissors':
            play_rock_paper_scissors(user_id)
        elif user_states[user_id] == 'playing_heads_or_tails':
            play_heads_or_tails(user_id)
    elif message.text.lower() == "выйти в меню":
        show_main_menu(user_id)
    else:
        bot.send_message(user_id, "Пожалуйста, выберите одну из предложенных кнопок.")

def play_rock_paper_scissors(user_id):
    global win_streak
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=3, resize_keyboard=True)
    rock_button = telebot.types.KeyboardButton('Камень')
    paper_button = telebot.types.KeyboardButton('Бумага')
    scissors_button = telebot.types.KeyboardButton('Ножницы')
    keyboard.add(rock_button, paper_button, scissors_button)
    bot.send_message(user_id, "Выберите свой вариант: Камень, ножницы или бумага?", reply_markup=keyboard)
    user_states[user_id] = 'playing_rock_paper_scissors'

# Обработчик для выбора варианта в игре "Камень, ножницы, бумага"
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'playing_rock_paper_scissors')
def handle_rock_paper_scissors_choice(message):
    global win_streak
    global win_record
    user_id = message.chat.id
    user_choice = message.text.lower()
    bot_choice = random.choice(['камень', 'ножницы', 'бумага'])

    result = determine_rps_winner(user_choice, bot_choice)
    tamagotchi = tamagotchis[user_id]

    if result == "Вы победили!":
        happiness_gain = random.randint(2, 5)
        tamagotchi.happiness += happiness_gain  # Увеличиваем счастье при победе (случайное число от 2 до 5)
        tamagotchi.happiness = min(100, tamagotchi.happiness)  # Ограничиваем значение счастья до 100
        win_streak[user_id] = win_streak.get(user_id, 0) + 1  # Увеличиваем победную серию
        if win_streak[user_id] > win_record.get(user_id, 0):
            win_record[user_id] = win_streak[user_id]  # Обновляем рекордную победную серию
        bot.send_message(user_id, f"Вы выбрали: {user_choice}\nБот выбрал: {bot_choice}\nРезультат: {result}\n"
                                  f"Поздравляю, вы выиграли и вашему {tamagotchi.pet_name} добавилось {happiness_gain} единиц счастья!\n"
                                  f"Текущая серия побед: {win_streak[user_id]}\nРекордная серия побед: {win_record[user_id]}")
    elif result == "Вы проиграли!":
        happiness_loss = random.randint(0, 3)
        tamagotchi.happiness -= happiness_loss  # Уменьшаем счастье при проигрыше (случайное число от 0 до 3)
        tamagotchi.happiness = max(0, tamagotchi.happiness)  # Ограничиваем значение счастья до 0
        win_streak[user_id] = 0  # Обнуляем победную серию
        bot.send_message(user_id, f"Вы выбрали: {user_choice}\nБот выбрал: {bot_choice}\nРезультат: {result}\n"
                                  f"К сожалению, вы проиграли и у вашего {tamagotchi.pet_name} было отнято {happiness_loss} единиц счастья.")
    else:
        # Для ничьей ничего не меняем
        bot.send_message(user_id, f"Вы выбрали: {user_choice}\nБот выбрал: {bot_choice}\nРезультат: {result}\n"
                                  f"Это ничья! Ничего не меняется.")

    show_end_game_menu(user_id)

    
    
def show_end_game_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    play_again_button = types.KeyboardButton("Сыграть заново")
    main_menu_button = types.KeyboardButton("Выйти в меню")
    keyboard.add(play_again_button, main_menu_button)

    bot.send_message(user_id, "Хотите сыграть заново или выйти в меню?", reply_markup=keyboard)
    user_states[user_id] = 'end_game'
    

def determine_rps_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "Ничья!"
    elif (user_choice == 'камень' and bot_choice == 'ножницы') or \
         (user_choice == 'ножницы' and bot_choice == 'бумага') or \
         (user_choice == 'бумага' and bot_choice == 'камень'):
        return "Вы победили!"
    else:
        return "Вы проиграли!"


def play_heads_or_tails(user_id):
    global win_streak
    keyboard = telebot.types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    heads_button = telebot.types.KeyboardButton('Орел')
    tails_button = telebot.types.KeyboardButton('Решка')
    keyboard.add(heads_button, tails_button)
    bot.send_message(user_id, "Выберите свой вариант: Орел или Решка?", reply_markup=keyboard)
    user_states[user_id] = 'playing_heads_or_tails'

# Обработчик для выбора варианта в игре "Орел и Решка"
@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'playing_heads_or_tails')
def handle_heads_or_tails_choice(message):
    global win_streak
    global win_record
    user_id = message.chat.id
    user_choice = message.text.lower()
    bot_choice = random.choice(['орел', 'решка'])

    result = determine_hot_winner(user_choice, bot_choice)
    tamagotchi = tamagotchis[user_id]

    if result == "Вы победили!":
        tamagotchi.happiness += 5  # Увеличиваем счастье при победе
        win_streak[user_id] = win_streak.get(user_id, 0) + 1  # Увеличиваем победную серию
        if win_streak[user_id] > win_record.get(user_id, 0):
            win_record[user_id] = win_streak[user_id]  # Обновляем рекордную победную серию
        bot.send_message(user_id, f"Вы выбрали: {user_choice}\nВыпало: {bot_choice}\nРезультат: {result}\n"
                                  f"Поздравляю, вы выиграли и вашему {tamagotchi.pet_name} добавилось 5 единиц счастья!\n"
                                  f"Текущая серия побед: {win_streak[user_id]}\nРекордная серия побед: {win_record[user_id]}")
    else:
        tamagotchi.happiness -= 3  # Уменьшаем счастье при проигрыше
        win_streak[user_id] = 0  # Обнуляем победную серию
        bot.send_message(user_id, f"Вы выбрали: {user_choice}\nВыпало: {bot_choice}\nРезультат: {result}\n"
                                  f"К сожалению, вы проиграли и у вашего {tamagotchi.pet_name} было отнято 3 единицы счастья.")
    
    show_end_game_menu(user_id)
    
def show_end_game_menu(user_id):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    play_again_button = types.KeyboardButton("Сыграть заново")
    main_menu_button = types.KeyboardButton("Выйти в меню")
    keyboard.add(play_again_button, main_menu_button)

    bot.send_message(user_id, "Хотите сыграть заново или выйти в меню?", reply_markup=keyboard)
    user_states[user_id] = 'end_game'
    bot.register_next_step_handler_by_chat_id(user_id, handle_end_game)

def handle_end_game(message):
    user_id = message.chat.id
    if message.text.lower() == "сыграть заново":
        show_play_menu(user_id)
    elif message.text.lower() == "выйти в меню":
        show_main_menu(user_id)


def determine_hot_winner(user_choice, bot_choice):
    if user_choice == bot_choice:
        return "Вы победили!"
    else:
        return "Вы проиграли!"


@bot.message_handler(commands=['help'])
def show_help(message):
    help_text = "Список доступных команд:\n"
    help_text += "/start - Создать тамагочи\n"
    help_text += "/play - Поиграть с тамагочи\n"
    help_text += "/feed - Кормить тамагочи\n"
    help_text += "/heal - Лечить тамагочи\n"
    help_text += "/job  - "
    bot.reply_to(message, help_text)

def decrease_stats():
    current_time = datetime.datetime.now()
    for user_id, tamagotchi in tamagotchis.items():
        time_passed = (current_time - tamagotchi.last_update_time).total_seconds() / 60  # Разница в минутах

        if time_passed >= 1:  # Уменьшать показатели каждые 2 минут
            tamagotchi.hunger -= random.randint(5, 10)  # Уменьшить голод на случайное количество
            tamagotchi.happiness -= random.randint(5, 10)  # Уменьшить счастье на случайное количество

            tamagotchi.hunger = max(0, tamagotchi.hunger)  # Гарантировать, чтобы голод не стал отрицательным
            tamagotchi.happiness = max(0, tamagotchi.happiness)  # Гарантировать, чтобы счастье не стало отрицательным

            tamagotchi.last_update_time = current_time  # Обновить время последнего обновления
            

bot.polling()