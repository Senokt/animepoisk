import os
from pymongo import MongoClient
import pymongo
from flask import Flask, request
from telebot import types

import telebot

TOKEN = '5218793149:AAGHJd7yVvzJXezTfQ0e77tnbStIpVWS99g'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

admins = []
password = "RanFer_add"
new_anime = {}
#подключение к бд
CONNECTION_STRING = "mongodb+srv://Senokt:Gunilya10@cluster0.s98e5.mongodb.net/myFirstDatabase?retryWrites=true&w=majority"
client = MongoClient(CONNECTION_STRING)
db = client['first_DB'] # first_DB - название базы данных
collection = db["anime"] # создаём коллекцию

@bot.message_handler(commands=['admin'])
def handle_command(message):
  bot.send_message(message.chat.id, 'Введите пароль, чтобы получить доступ к панели администратора')
  bot.register_next_step_handler(message, check)

def check(message):
  if message.text == password:
    admins.append(message.from_user.id)
    bot.send_message(message.chat.id, 'Вы успешно вошли в роли админа')
  else:
    bot.send_message(message.chat.id, 'Неверный пароль')

@bot.message_handler(commands=['add'])
def add(message):
  if message.chat.id in admins:
    bot.send_message(message.chat.id, 'Начинаем процесс добавления аниме')
    bot.send_message(message.chat.id, 'Введите id аниме: ')
    bot.register_next_step_handler(message, add1)

#сохраняет название, запрашивает жанр
def add1(message):
  new_anime.update({"id": int(message.text)})
  bot.send_message(message.chat.id, 'Введие Название Аниме: ')
  bot.register_next_step_handler(message, add2)


def add2(message):
  new_anime.update({"Название": message.text})
  bot.send_message(message.chat.id, 'Введите сезон аниме: ')
  bot.register_next_step_handler(message, add3)

#сохраняет жанр, запрашивает рейтинг
def add3(message):
  new_anime.update({"Сезоны": message.text})
  bot.send_message(message.chat.id, 'Введите количество Серии аниме: ')
  bot.register_next_step_handler(message, add4)

def add4(message):
  new_anime.update({"Серии": message.text})
  bot.send_message(message.chat.id, 'Введите Жанр аниме: ')
  bot.register_next_step_handler(message, add5)

def add5(message):
  new_anime.update({"Жанр": message.text})
  bot.send_message(message.chat.id, 'Введите рейтинг аниме: ')
  bot.register_next_step_handler(message, add6)

def add6(message):
  new_anime.update({"Рейтинг": float(message.text)})
  bot.send_message(message.chat.id, 'Видите Описание аниме: ')
  bot.register_next_step_handler(message, add7)

def add7(message):
  new_anime.update({"Описание": (message.text)})
  bot.send_message(message.chat.id, 'Вы успешно добавили аниме')  
  print(new_anime)
  collection.insert_one(new_anime)


@bot.message_handler(commands=['help'])
def handle_command(message):
  # создаём клавиатуру и кнопки
  bot.send_message(message.chat.id, 'Привет, зачем же ты меня призвал?') # привязываем клавиатуру к сообщению

# переделайте функцию, чтобы она отправляла данные от лица бота, а не выводила в консоль
@bot.message_handler(commands=['all'])
def all_films(message):
  films = collection.find() # находим все данные из коллекции при помощи метода find()
  for film in films:
      # Выводим все фильмы
      z = "Название: " +film["Название"] + "\n"+ "Рейтинг: " + str(film["Рейтинг"]) + "\n" + "Жанр: " + film["Жанр"] + "\n" + "Серии: " + str(film["Серии"]) + "\n" + "Сезон: " + film["Сезон"] + "\n" + "Описание: " + film["Описание"]
      bot.send_message(message.chat.id,"Название фильма:"+ z)

@bot.message_handler(commands=['random'])
def random_anime(message):
  films = collection.find() 
  d = []
  for i in films:
    d.append(i)
  x =  random.choice(d)

  bot.send_message(message.chat.id, x["Название"]) # привязываем клавиатуру к сообщению

@bot.message_handler(commands=['rating'])
def best_anime(message):
  films = collection.find()
  maxx = -1
  bestFilm=None
  for film in films:
    if film["Рейтинг"]>= maxx:
      maxx = film["Рейтинг"]
      bestFilm = film
  bot.send_message(message.chat.id, bestFilm["Название"])

@server.route('/' + TOKEN, methods=['POST'])
def getMessage():
    json_string = request.get_data().decode('utf-8')
    update = telebot.types.Update.de_json(json_string)
    bot.process_new_updates([update])
    return "!", 200
    
@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url='https://animepoisk.herokuapp.com/' + TOKEN)
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))
