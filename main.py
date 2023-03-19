import config
import telebot
from telebot.types import InlineKeyboardButton, InlineKeyboardMarkup
import requests
from bs4 import BeautifulSoup

#Получим курс доллра к рублю
url = 'https://www.x-rates.com/calculator/?from=USD&to=RUB&amount=1'
page = requests.get(url)
#print(page.status_code)
soup = BeautifulSoup(page.text, 'lxml')

rate = soup.find('span', class_='ccOutputRslt')

bot = telebot.TeleBot(config.TOKEN)

transaction_income = {}

def start_button(message):
    bot.send_sticker(message.chat.id, 'CAACAgIAAxkBAAEIM3lkF2sJvI4aQHHkxciKpHWdHrWZ5wACzBAAAr8M0ErYqDe37o7zay8E')
    keyboard = InlineKeyboardMarkup()
    keyboard.row(InlineKeyboardButton('💸 Доходы', callback_data='income'),
                 InlineKeyboardButton('💸 Расходы', callback_data='expense'))
    bot.send_message(message.chat.id, f'🇺🇸➡️🇷🇺 Текущий курс доллара к рублю: {rate.text}')
    bot.send_message(message.chat.id, '🔔️ Пожалуйста, выберите категорию:', reply_markup=keyboard)


def continue_button(message, button_id):
    keyboard = InlineKeyboardMarkup()
    keyboard.row(
        InlineKeyboardButton('🔄 Добавить еще сумму', callback_data=button_id)
    )
    keyboard.row(
        InlineKeyboardButton('🔙 Вернуться к главному меню', callback_data='main_menu')
    )
    bot.send_message(message.chat.id, f'💬 Что дальше?', reply_markup=keyboard)

@bot.message_handler(commands=['start'])
def start(message):
  bot.send_message(message.chat.id, f'Привет👋 \nДанный бот поможет тебе следить за доходами и расходами.')
  start_button(message)


@bot.callback_query_handler(func=lambda call: True)
def button_click(callback_query):
  button_id = callback_query.data
  chat_id = callback_query.message.chat.id
  message = callback_query.message
  if button_id == 'income':
      keyboard = InlineKeyboardMarkup()
      keyboard.row(
          InlineKeyboardButton('💸 Зарплата', callback_data='salary'),
          InlineKeyboardButton('💸 Прочее', callback_data='other_income')
      )
      keyboard.row(
          InlineKeyboardButton('🔙 Вернуться к главному меню', callback_data='main_menu')
      )

      #здесь можно написать какие инлайн кнопки вывести
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id, reply_markup=None)
      bot.send_message(callback_query.message.chat.id, f'✔️ Вы выбрали категорию "Доходы"!', reply_markup=keyboard)

  elif button_id == 'expense':
      keyboard = InlineKeyboardMarkup()
      keyboard.row(
          InlineKeyboardButton('💸 Важные расходы', callback_data='important_expense'),
          InlineKeyboardButton('💸 Прочее', callback_data='other_expense')
      )
      keyboard.row(
          InlineKeyboardButton('🔙 Вернуться к главному меню', callback_data='main_menu')
      )
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                    reply_markup=None)
      bot.send_message(callback_query.message.chat.id, f'✔️ Вы выбрали категорию "Расходы"!', reply_markup=keyboard)

  elif button_id == 'main_menu':
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                    reply_markup=None)
      start_button(callback_query.message)

  elif button_id == 'salary':
      #transaction_income[button_id] = 0
      bot.send_message(message.chat.id, '💬 Пожалуйста, введите сумму:')
      bot.register_next_step_handler(message, income_amount, additional_arg = button_id)
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id, reply_markup=None)

  elif button_id == 'other_income':
      bot.send_message(message.chat.id, '💬 Пожалуйста, введите сумму:')
      bot.register_next_step_handler(message, income_amount, additional_arg = button_id)
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                    reply_markup=None)
  elif button_id == 'important_expense':
      bot.send_message(message.chat.id, '💬 Пожалуйста, введите сумму:')
      bot.register_next_step_handler(message, income_amount, additional_arg = button_id)
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                    reply_markup=None)
  elif button_id == 'other_expense':
      bot.send_message(message.chat.id, '💬 Пожалуйста, введите сумму:')
      bot.register_next_step_handler(message, income_amount, additional_arg = button_id)
      bot.edit_message_reply_markup(callback_query.message.chat.id, callback_query.message.message_id,
                                    reply_markup=None)

def income_amount(message, **kwargs):
    button_id = kwargs.get('additional_arg')
    try:
        amount = float(message.text)
        # Update the transactions dictionary with the income amount
        if button_id in transaction_income:
            transaction_income[button_id] += amount
        else:
            transaction_income[button_id] = amount
        # Send a success message to the user
        bot.send_message(message.chat.id, f"✔️ Сумма {amount} руб. успешно добавлена")
        bot.send_message(message.chat.id, f"💰 Общая сумма в данной категории: {transaction_income[button_id]} руб.")

    except ValueError:
    # Send an error message to the user if the input is not a number
        bot.send_message(message.chat.id, "⚠️ Ошибка. Пожалуйста, введите число")
    continue_button(message, button_id)


bot.polling()