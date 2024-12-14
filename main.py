import random, telebot, pandas, os, numpy, yaml
import cryptpandas as crp
from telebot import types

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))

with open('config.yaml') as f:
	config = yaml.safe_load(f)
bot = telebot.TeleBot(config['token'])

answers = ['Я не понял, что ты хочешь сказать.', 'Извини, я тебя не понимаю.', 'Я не знаю такой команды.', '>_<', '>:(']

needed=0.0
num_of_scores = {'5':0, '4':0, '3':0, '2':0, '1':0, 'needed':0.0}

lastPhotoIndex = -1

level = 'menu'

photo = {'ID': [], 'Description': [], 'Name': [], 'Info':[]}

shortener = ['two', 'three', 'four', 'five']

buttons = {
    'button_back' : types.InlineKeyboardButton('↩️ Назад', callback_data = 'back'),
	'button_back1' : types.InlineKeyboardButton('↩️ Назад', callback_data = 'back1'),
	'button_menu' : types.InlineKeyboardButton('↩️ В меню', callback_data = 'menu'),
	'button_begin' : types.InlineKeyboardButton('📈 Рассчитать необходимое количество оценок', callback_data = 'begin'),
	'button_info' : types.InlineKeyboardButton('📄 Справка', callback_data = 'info'),
	'button_admin' : types.InlineKeyboardButton('🔐 Войти, как админ', callback_data = 'admin'),
	'button_more' : types.InlineKeyboardButton('📄 Ещё', callback_data = 'more'),
    'button_more_pic' : types.InlineKeyboardButton('🖼️ Ещё', callback_data = 'more_pic'),
	'button_shitpost' : types.InlineKeyboardButton('💀 Прислать пикчу', callback_data = 'shitpost'),
	'button2' : types.InlineKeyboardButton('2️⃣ 1.8', callback_data = 'two'),
	'button3' : types.InlineKeyboardButton('3️⃣ 2.7', callback_data = 'three'),
	'button4' : types.InlineKeyboardButton('4️⃣ 3.6', callback_data = 'four'),
	'button5' : types.InlineKeyboardButton('5️⃣ 4.5', callback_data = 'five'),
	'button_other' : types.InlineKeyboardButton('📝 Другой', callback_data = 'other'),
    'button_about' : types.InlineKeyboardButton('С описанием', callback_data = 'aboutPhoto'),
	'button_skip' : types.InlineKeyboardButton('Без описания', callback_data = 'skip'),
    'button_nametag' : types.InlineKeyboardButton('🔐 параметры отображения имени', callback_data = 'nametag')
    
}

try:
    # creates db if it didn't exist
	decrypted_df = crp.read_encrypted(path=os.path.join(__location__,'admins.crypt'), password=config['admin_pass'])
except FileNotFoundError:
    df = pandas.DataFrame({'ID': [], 'Name': [], 'ShowNametag': []})
    crp.to_encrypted(df, password=config['admin_pass'], path=os.path.join(__location__,'admins.crypt'))
try:
    # creates db if it didn't exist
	df = pandas.read_csv(os.path.join(__location__, 'photos.csv'))
except FileNotFoundError:
    df = pandas.DataFrame({'ID': [], 'Description': [], 'Name': [], 'Info':[]})
    df.to_csv(os.path.join(__location__, 'photos.csv'))


# Обработка команды /start
@bot.message_handler(commands=['start', 'menu'])
def welcome(message):
    global buttons
    markup = types.InlineKeyboardMarkup(row_width=2)
    markup.add(buttons['button_begin'])
    markup.add(buttons['button_info'])

    if message.text == '/start':
        # Отправляю приветственный текст
        bot.send_message(message.chat.id, f'Привет, {message.from_user.first_name}!\nУ меня ты сможешь рассчитать необходимое количество оценок!', reply_markup=markup)
    else:
        bot.send_message(message.chat.id, 'Что теперь?', reply_markup=markup)

# Обработка фото. Если пользователь пришлет фото, то бот отреагирует на него. Можно реализовать свой функционал
@bot.message_handler(content_types='photo')
def get_photo(message):
	global photo, row, buttons

	markup = types.InlineKeyboardMarkup(row_width=2)
	markup.add(buttons['button_menu'])
	df = crp.read_encrypted(path=os.path.join(__location__,'admins.crypt'), password=config['admin_pass'])
	user_id = message.from_user.id
	if user_id in df.ID.tolist():
		photos_df = pandas.read_csv(os.path.join(__location__,'photos.csv'))
		info = bot.get_file(message.photo[-1].file_id).file_path
		if info in photos_df.Info.tolist():
			bot.send_message(message.chat.id, 'Такое уже есть', reply_markup = markup)
		else:
			photo = {'ID': [], 'Description': [], 'Name': [], 'Info':[]}

			photo['ID'] = [message.photo[-1].file_id]
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			decrypted_df.set_index('ID', inplace=True)
			cond = decrypted_df._get_value(message.from_user.id, 'ShowNametag')  == 1

			if cond:
				photo['Name'] = [message.from_user.first_name]
			else:
				photo['Name'] = ["<admin>"]
			photo['Info'] = [info]
			markup_c = types.InlineKeyboardMarkup(row_width=2)
			markup_c.add(buttons['button_about'], buttons['button_skip'])
			bot.send_message(message.chat.id, 'Параметры фото', reply_markup = markup_c)


	else:
		bot.send_message(message.chat.id, 'У меня нет возможности просматривать твои фото :(', reply_markup = markup)

def enter_descr(message):
	global photo, buttons
	markup_some = types.InlineKeyboardMarkup(row_width=2)
	markup_some.add(buttons['button_menu'])
	photos_df = pandas.read_csv(os.path.join(__location__, 'photos.csv'))
	photo['Description'] = [message.text.strip()]
	print(type(message.text.strip()))
	row = pandas.DataFrame(photo)
	photos_df = pandas.concat([photos_df, row])
	photos_df.to_csv(os.path.join(__location__, 'photos.csv'))
	bot.send_message(message.chat.id, 'Добавлено', reply_markup = markup_some)


@bot.callback_query_handler(func = lambda call:True)
def answer(callback):
	global level, needed, photo, lastPhotoIndex, buttons
	new_text = ''

	markup_call = types.InlineKeyboardMarkup(row_width=2)

	if callback.message:

		if callback.data == 'begin':
			level = 'menu'
			markup_call.add(buttons['button5'], buttons['button4'])
			markup_call.add(buttons['button3'], buttons['button2'])
			markup_call.add(buttons['button_other'])
			markup_call.add(buttons['button_menu'])
			new_text = "Какой балл нужен?"
		elif callback.data == 'aboutPhoto':
			msg = bot.send_message(callback.message.chat.id, 'Введите описание')
			bot.register_next_step_handler(msg, enter_descr)

		elif callback.data == 'skip':
			markup_call.add(buttons['button_menu'])
			print(callback.message.text.strip())
			photos_df = pandas.read_csv(os.path.join(__location__, 'photos.csv'))
			stroc = "----"
			photo['Description'] = [stroc]
			row = pandas.DataFrame(photo)
			photos_df = pandas.concat([photos_df, row])
			photos_df.to_csv(os.path.join(__location__, 'photos.csv'))
			bot.send_message(callback.message.chat.id, 'Добавлено', reply_markup = markup_call)

		elif callback.data == 'shitpost' or callback.data == 'more_pic':
			level = 'info'
			markup_call.add(buttons['button_more_pic'], buttons['button_back1'])
			photos_df = pandas.read_csv(os.path.join(__location__, 'photos.csv'))
			plist = photos_df.ID.tolist()
			ulist = photos_df.Name.tolist()
			dlist = photos_df.Description.tolist()
			ind = random.randint(0, len(plist)-1)
			count = 0
			while ind == lastPhotoIndex and count != 10:
				ind = random.randint(0, len(plist)-1)
				count += 1
			print(dlist[ind])
			if dlist[ind] == "----":
				bot.send_photo(callback.message.chat.id, plist[ind], reply_markup = markup_call, caption = f"By: {ulist[ind]}")
			else:
				bot.send_photo(callback.message.chat.id, plist[ind], reply_markup = markup_call, caption = f"Описание: {str(dlist[ind])}\nBy: {ulist[ind]}")
			new_text = ''

		elif callback.data == 'back1':
			back(callback.message, 1, level)
		elif callback.data == 'back':
			back(callback.message, 0, level)

		elif callback.data == 'info':
			level = 'menu'
			markup_call.add(buttons['button_shitpost'])
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			if callback.from_user.id in decrypted_df.ID.tolist():
				markup_call.add(buttons['button_nametag'])
			else:
				markup_call.add(buttons['button_admin'])
			markup_call.add(buttons['button_back'])
			new_text = 'Раздел справки.\nБот рассчитывающий, сколько оценок осталось получить.'

		elif callback.data == 'more':
			level = 'info'
			markup_call.add(buttons['button_back'])
			new_text = 'А больше ничего пока нет'

		elif callback.data == 'nametag':
			level = 'info'
			new_text = "Сейчас твоё имя "
			option = ''

			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			decrypted_df.set_index('ID', inplace=True)
			cond = decrypted_df._get_value(callback.from_user.id, 'ShowNametag')  == 1
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])

			if cond:
				new_text += 'Видно всем'
				option = 'Скрыть'
			else:
				new_text += 'Скрыто'
				option = 'Показать'
			button_show = types.InlineKeyboardButton(f'{option}', callback_data = 'showSet')
			markup_call.add(button_show)
			markup_call.add(buttons['button_back'])

		elif callback.data == 'showSet':

			new_text = 'Теперь твоё имя '

			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			decrypted_df.set_index('ID', inplace=True)
			cond = decrypted_df._get_value(callback.from_user.id, 'ShowNametag')  == 1
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])

			if cond:
				decrypted_df['ShowNametag'] = numpy.where(decrypted_df["ID"] == callback.from_user.id, 0, decrypted_df['ShowNametag'])
				new_text += 'скрыто'
			else:
				new_text += 'видно всем'
				decrypted_df['ShowNametag'] = numpy.where(decrypted_df["ID"] == callback.from_user.id, 1, decrypted_df['ShowNametag'])
			crp.to_encrypted(decrypted_df, password=config['admin_pass'], path=os.path.join(__location__, 'admins.crypt'))
			markup_call.add(buttons['button_back'])

		elif callback.data == 'admin':
			level = 'info'
			markup_call.add(buttons['button_back'])
			markup_call.add(buttons['button_menu'])
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			if callback.from_user.id in decrypted_df.ID.tolist():
				new_text = "Ты уже администратор"
			else:
				msg = bot.edit_message_text(text='Введти пароль администратора',
	                                  chat_id=callback.message.chat.id,
	                                  message_id=callback.message.message_id,
	                                  reply_markup = markup_call)
				bot.register_next_step_handler(msg, enter_pass)

		elif callback.data == 'menu':
			markup_call.add(buttons['button_begin'])
			markup_call.add(buttons['button_info'])
			new_text = 'Что теперь?'

		elif callback.data == 'other':
			level = 'other'
			markup_call.add(buttons['button_back'])
			msg = bot.edit_message_text(text='Какой балл нужен?',
                                  chat_id=callback.message.chat.id,
                                  message_id=callback.message.message_id,
                                  reply_markup = markup_call)
			bot.register_next_step_handler(msg, enter_needed)

		elif callback.data in shortener:
			level = 'begin'
			markup_call.add(buttons['button_back'])
			markup_call.add(buttons['button_menu'])
			match callback.data:
				case 'two':
					num_of_scores['needed'] = 1.8
				case 'three':
					num_of_scores['needed'] = 2.7
				case 'four':
					num_of_scores['needed'] = 3.6
				case 'five':
					num_of_scores['needed'] = 4.5
			msg = bot.edit_message_text(text='Cколько 5?',
                                  chat_id=callback.message.chat.id,
                                  message_id=callback.message.message_id,
                                  reply_markup = markup_call)
			bot.register_next_step_handler(msg, enterScore, 5)
			new_text = ''
		if callback.message.text != new_text and new_text != '':
			bot.edit_message_text(text=new_text,
                                    chat_id=callback.message.chat.id,
                                    message_id=callback.message.message_id,
                                    reply_markup=markup_call)

def enter_pass(message):
	global buttons
	markup_some = types.InlineKeyboardMarkup(row_width=2)
	button_back = types.InlineKeyboardButton('↩️ Назад', callback_data = 'back')
	button_menu = types.InlineKeyboardButton('↩️ В меню', callback_data = 'menu')
	markup_some.add(buttons['button_back'])
	markup_some.add(buttons['button_menu'])
	print(message.text.strip(), message.text)
	try:
		decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=message.text.strip())
		row = pandas.DataFrame({'ID': [message.from_user.id], 'Name':[message.from_user.first_name], 'ShowNametag': [1]})
		decrypted_df = pandas.concat([decrypted_df, row])
		crp.to_encrypted(decrypted_df, password=config['admin_pass'], path=os.path.join(__location__, 'admins.crypt'))
		bot.send_message(message.chat.id, 'Готово', reply_markup = markup_some)

	except:
		bot.send_message(message.chat.id, '🔴 Oh Hell Nah', reply_markup = markup_some)

def back(message, ind, lvl):

	global level, buttons
	print(lvl, level)
	markup_call = types.InlineKeyboardMarkup(row_width=2)
	match lvl:
		case 'info':
			level = 'menu'
			markup_call.add(buttons['button_shitpost'])
			decrypted_df = crp.read_encrypted(path=os.path.join(__location__, 'admins.crypt'), password=config['admin_pass'])
			if message.from_user.id in decrypted_df.ID.tolist():
				markup_call.add(buttons['button_nametag'])
			else:
				markup_call.add(buttons['button_admin'])
			markup_call.add(buttons['button_back'])
			new_text = 'Раздел справки.\nБот рассчитывающий, сколько оценок осталось получить.'
		case 'begin':
			level = 'menu'
			markup_call.add(buttons['button5'], buttons['button4'])
			markup_call.add(buttons['button3'], buttons['button2'])
			markup_call.add(buttons['button_other'])
			markup_call.add(buttons['button_menu'])
			new_text = "Какой балл нужен?"
		case 'menu':
			markup_call.add(buttons['button_begin'])
			markup_call.add(buttons['button_info'])
			new_text = 'Что теперь?'
		case 'five':
			level = 'begin'
			enterScore('back', 5)
		case 'four':
			level = 'five'
			enterScore('back', 4)
		case 'three':
			level = 'four'
			enterScore('back', 3)
		case 'two':
			level = 'two'
			enterScore('back', 2)
	if ind == 1:
		bot.send_message(message.chat.id, new_text, reply_markup = markup_call)
	elif message.text != new_text and new_text != '':
		bot.edit_message_text(text=new_text,
                                chat_id=message.chat.id,
                                message_id=message.message_id,
                                reply_markup=markup_call)

def enterScore(message, number):
    global buttons
    number = int(number)
    cases = ['begin', 'five', 'four', 'three', 'two']

    markup_some = markup_call = types.InlineKeyboardMarkup()
    markup_some.add(buttons['button_back'])
    markup_some.add(buttons['button_menu'])
    level = cases[5-number]
    if number>1:
        if message == 'back':
            bot.send_message(message.chat.id, f"Cколько {number-1}?", reply_markup = markup_some)
            bot.register_next_step_handler(message, enterScore, number-1)
        else:
            if message.text.strip().isdigit() and int(message.text.strip())>=0:
                num_of_scores[str(number)]=int(message.text.strip())
                bot.send_message(message.chat.id, f"Cколько {number-1}?", reply_markup = markup_some)
                bot.register_next_step_handler(message, enterScore, number-1)
            else:
                bot.send_message(message.chat.id, 'Suck: не целое число')
                back(message, 1, level)
    else:
        if message == 'back':
            bot.send_message(message.chat.id, "Cколько 1?", reply_markup = markup_some)
            bot.register_next_step_handler(message, enterScore, 3)
        else:
            if message.text.strip().isdigit() and int(message.text.strip())>=0:
                num_of_scores[str(number)]=int(message.text.strip())
                textic = score(num_of_scores)
                bot.send_message(message.chat.id, textic, reply_markup = markup_some)
            else:
                bot.send_message(message.chat.id, 'Suck: не целое число')
                back(message, 1, level)


def enter_needed(message):
	global buttons, num_of_scores
	markup_some = markup_call = types.InlineKeyboardMarkup()
	markup_some.add(buttons['button_back'])
	level = 'begin'

	mess = message.text.strip()
	print(mess)
	ann = False


	if "," in message.text.strip():
		mess = mess.replace(',', '.', 1)
	if mess.isdigit():
		ann = True
	else:
		try:
			float(mess)
			ann = True
		except ValueError:
			ann = False

	if ann:
		needed = float(mess)
		if needed<=5.0 and 1.0<=needed:
			num_of_scores['needed'] = needed
			bot.send_message(message.chat.id, "Cколько 5?", reply_markup = markup_some)
			bot.register_next_step_handler(message, enterScore, 5)
		else:
			bot.send_message(message.chat.id, 'Suck: Недопустимое значение')
			back(message, 1, level)
	else:
		bot.send_message(message.chat.id, 'Suck: не вещественное число')
		back(message, 1, level)


def score( num_of_scores):
	n5 = 0
	n4 = 0
	n3 = 0
	n2 = 0
	summ = 5 * num_of_scores['5'] + 4 * num_of_scores['4'] + num_of_scores['3'] * 3 + 2 * num_of_scores['2'] + num_of_scores['1']
	sum2m = num_of_scores['5'] + num_of_scores['4'] + num_of_scores['3'] + num_of_scores['2'] + num_of_scores['1']
	ball = summ / sum2m
	print(num_of_scores)
	if num_of_scores['needed']>5.0:
		return "Suck: >5"

	if num_of_scores['needed'] < 5.0:
	    sum = summ
	    sum2 = sum2m
	    while ball < num_of_scores['needed']:
	        sum += 5
	        sum2 += 1
	        ball = sum / sum2
	        n5 += 1

	ball = summ / sum2m
	if num_of_scores['needed'] < 4.0:
	    sum = summ
	    sum2 = sum2m
	    while ball < num_of_scores['needed']:
	        sum += 4
	        sum2 += 1
	        ball = sum / sum2
	        n4 += 1

	ball = summ / sum2m

	if num_of_scores['needed']<3.0:
	    sum = summ
	    sum2 = sum2m
	    while ball < num_of_scores['needed']:
	        sum += 3
	        sum2 += 1
	        ball = sum / sum2
	        n3 += 1

	ball = summ / sum2m

	if num_of_scores['needed'] < 2.0:
	    sum = summ
	    sum2 = sum2m
	    while ball < num_of_scores['needed']:
	        sum += 2
	        sum2 += 1
	        ball = sum / sum2
	        n2 += 1
	textic = f"Kол-во 5: {n5}\nKол-во 4: {n4}\nKол-во 3: {n3}\nKол-во 2: {n2}"

	return textic


bot.infinity_polling(none_stop=True)