import sqlite3
from telegram import Update
from datetime import datetime
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, ConversationHandler

CHOOSING_ACTION, ASKING_SIDE_EFFECT, ASKING_DRUG_NAME, ASKING_MANUFACTURER, ASKING_FORM, ASKING_BATCH_NUMBER, ASKING_DRUG_SEARCH = range(7)

def start(update, context):
    update.message.reply_text(
        "Привет! Я бот \"Неблагоприятные побочные реакции лекарственных средств\".\n"
        "Введите 1, если хотите зарегистрировать побочный эффект, "
        "или введите 2, если хотите узнать о побочных эффектах по наименованию"
    )
    return CHOOSING_ACTION

def handle_action_choice(update, context):
    choice = update.message.text
    if choice == "1":
        update.message.reply_text("Укажите побочный эффект:")
        return ASKING_SIDE_EFFECT
    elif choice == "2":
        update.message.reply_text("Укажите наименование препарата:")
        return ASKING_DRUG_SEARCH
    else:
        update.message.reply_text("Пожалуйста, выберите 1 или 2.")
        return CHOOSING_ACTION

def handle_side_effect(update, context):
    side_effect = update.message.text
    context.user_data['side_effect'] = side_effect
    update.message.reply_text("Укажите наименование препарата:")
    return ASKING_DRUG_NAME

def handle_drug_name(update, context):
    drug_name = update.message.text
    context.user_data['drug_name'] = drug_name
    update.message.reply_text("Укажите производителя препарата:")
    return ASKING_MANUFACTURER

def handle_manufacturer(update, context):
    manufacturer = update.message.text
    context.user_data['manufacturer'] = manufacturer
    update.message.reply_text("Укажите форму выпуска препарата:")
    return ASKING_FORM

def handle_form(update, context):
    form = update.message.text
    context.user_data['form'] = form
    update.message.reply_text("Укажите номер серии/партии препарата:")
    return ASKING_BATCH_NUMBER

def handle_batch_number(update, context):
    batch_number = update.message.text
    form = context.user_data['form']
    context.user_data['batch_number'] = batch_number

    side_effect = context.user_data.get('side_effect')
    drug_name = context.user_data.get('drug_name')
    manufacturer = context.user_data.get('manufacturer')
    form = context.user_data.get('form')
    batch_number = context.user_data.get('batch_number')

    if side_effect:
        conn = sqlite3.connect('side_effects3.db')
        c = conn.cursor()
        user_id = update.message.from_user.id
        c.execute('''CREATE TABLE IF NOT EXISTS side_effects3 (
                     user_id INTEGER,
                     category TEXT,
                     description TEXT,
                     manufacturer TEXT,
                     form TEXT,
                     batch_number TEXT)''')
        c.execute("INSERT INTO side_effects3 (user_id, category, description, manufacturer, form, batch_number) VALUES (?, ?, ?, ?, ?, ?)",
                  (user_id, side_effect, drug_name, manufacturer, form, batch_number))
        conn.commit()
        conn.close()

        update.message.reply_text(f"Спасибо! Побочный эффект '{side_effect}' при использовании препарата '{drug_name}' от производителя '{manufacturer}' в форме '{form}' с номером серии/партии '{batch_number}' зарегистрирован.")
    else:
        update.message.reply_text(f"Производитель: {manufacturer}\n"
                                  f"Форма выпуска: {form}\n"
                                  f"Номер серии/партии: {batch_number}")
    return ConversationHandler.END

def handle_drug_search(update, context):
    drug_name = update.message.text
    
    conn = sqlite3.connect('side_effects3.db')
    c = conn.cursor()
    c.execute("SELECT * FROM side_effects3 WHERE description=?", (drug_name,))
    data = c.fetchall()
    conn.close()
    
    if data:
        response = ""
        for row in data:
            response += f"Категория: {row[1]}\n"
            response += f"Производитель: {row[3]}\n"
            response += f"Форма: {row[4]}\n"
            response += f"Номер серии/партии: {row[5]}\n\n"
        update.message.reply_text(response)
    else:
        update.message.reply_text("К сожалению, данные на этот препарат отсутствуют.")

    return ConversationHandler.END

def main():
    updater = Updater("6673952291:AAGsb_u1nv2QRlP9Iw4tyVGX5bpBFQEbo9A", use_context=True)
    dp = updater.dispatcher
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            CHOOSING_ACTION: [MessageHandler(Filters.text & ~Filters.command, handle_action_choice)],
            ASKING_SIDE_EFFECT: [MessageHandler(Filters.text & ~Filters.command, handle_side_effect)],
            ASKING_DRUG_NAME: [MessageHandler(Filters.text & ~Filters.command, handle_drug_name)],
            ASKING_MANUFACTURER: [MessageHandler(Filters.text & ~Filters.command, handle_manufacturer)],
            ASKING_FORM: [MessageHandler(Filters.text & ~Filters.command, handle_form)],
            ASKING_BATCH_NUMBER: [MessageHandler(Filters.text & ~Filters.command, handle_batch_number)],
            ASKING_DRUG_SEARCH: [MessageHandler(Filters.text & ~Filters.command, handle_drug_search)],
        },
        fallbacks=[]
    )
    dp.add_handler(conv_handler)
    
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()

