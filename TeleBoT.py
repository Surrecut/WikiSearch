import telebot
from telebot import types
import wikipedia
from bs4 import BeautifulSoup

# Русcификатор для текста c Wiki
wikipedia.set_lang('ru')

# id для работы с ботом
bot = telebot.TeleBot('Токен бота')

# Выводит приветственное сообщение
@bot.message_handler(commands=['start'])
def main(message):
    # Вывод приветственного сообщения
    bot.send_message(message.chat.id,
                     f'<b>Привет</b> <b>{message.from_user.first_name}</b>, SiteLib - это Библиотека сайтов! Здесь вы можете найти официальные ссылки на интересующие вас сайты и их небольшое описание.',
                     parse_mode='html')
    # Кнопки
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    # Создание кнопок
    btn1 = types.KeyboardButton('Поиск')
    markup.add(btn1)
    # Вывод сообщения
    bot.send_message(message.chat.id, 'Выберите действие', reply_markup=markup)
    # Нажатие на кнопку
    bot.register_next_step_handler(message, on_click)


@bot.message_handler(commands=['Поиск'])
def on_click(message):
    # После нажатия кнопки
    if message.text == 'Поиск':
        # Вывод сообщения
        bot.send_message(message.chat.id, 'Введи название сайта для поиска:')
        bot.register_next_step_handler(message, get_info)


@bot.message_handler(commands=['get_info'])
def get_info(message):
    # Получение информации о сайте
    site = message.text.strip().lower()
    try:
        # Получение официального сайта
        res = wikipedia.summary(site, sentences=2)
        official_website = get_official_website_url(site)
        if official_website:
            # Создание кнопки
            markup = types.InlineKeyboardMarkup()
            markup.add(types.InlineKeyboardButton("Сайт", url=official_website))
            # Вывод описания
            bot.reply_to(message, f'{res}', reply_markup=markup)
            # Если официальный сайт не найден
        else:
            bot.reply_to(message, 'Официальный сайт не найден.')
    except wikipedia.exceptions.DisambiguationError as e:
        bot.reply_to(message, f'Пожалуйста, уточните запрос для сайта "{site}".')
    except wikipedia.exceptions.PageError as e:
        bot.reply_to(message, f'Информация о сайте "{site}" не найдена.')

    # Возвращаемся к функии поиска
    bot.register_next_step_handler(message, get_info)


def get_official_website_url(page_title):
    # Получаем HTML-код страницы Википедии
    page_html = wikipedia.page(page_title).html()

    # Используем BeautifulSoup для парсинга HTML
    soup = BeautifulSoup(page_html, 'html.parser')

    # Находим блок справа, содержащий информацию о статье
    sidebar = soup.find('table', class_='infobox')

    if sidebar:
        # Находим все ссылки в блоке справа
        all_links = sidebar.find_all('a', class_='external text')

        # Проверяем каждую ссылку
        for link in all_links:
            # Настройка поиска ссылки
            if ('href' in link.attrs and link.attrs['href'].startswith('http://') or link.attrs['href'].startswith('https://')
                    # Исключения
                    and 'ru.wikipedia' not in link.attrs['href']
                    and 'git' not in link.attrs['href']
                    and 'nasdaq' not in link.attrs['href']
                    and 'nyse' not in link.attrs['href']
                    and 'moex.com' not in link.attrs['href']
                    and 'sourceforge' not in link.attrs['href']):
                # Вывод официального сайта
                official_website_link = link.attrs['href']
                return official_website_link

# Запуск бота
bot.infinity_polling()