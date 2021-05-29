import os
import logging
from settings import TELEGRAM_TOKEN
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
from telegram.ext import (
    Updater,
    CommandHandler,
    MessageHandler,
    Filters,
    ConversationHandler,
    CallbackContext,
)

from settings import WELCOME_MESSAGE, TELEGRAM_SUPPORT_CHAT_ID

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)

NAME,WELCOME, CHOISE_CREDIT_OR_EAT,HAVE_QUESTION,CHOSING, END, ANYHELP, TO_USER = range(8)


menubutton1 ='Хочу возместить проценты по кредиту'
menubutton2 ='Хочу возместить комиссию за доставку'

menu = ReplyKeyboardMarkup([[menubutton1],[menubutton2]], resize_keyboard=True)


creditbutton1 = 'У ведомить меня о старте программы'
creditbutton2 = 'У меня остались вопросы'

info_for_start_program = ReplyKeyboardMarkup([[creditbutton1],[creditbutton2]], resize_keyboard=True)


call_me = 'Позвоните мне'
i_call = 'Позвоню сам'

question_keyboard = ReplyKeyboardMarkup([[call_me],[i_call]],resize_keyboard=True)


#По команде /start, начинает отрабатывать функция и возвращаем reply_text
def start(update:Update, context: CallbackContext):
    user_info = update.message.from_user.to_dict()
    if update.message.chat.type == 'private':
        reply_text ='Добрый день! Вас приветствует ГКУ «Центр реализации программ поддержки и развития малого и среднего предпринимательства Республики Татарстан».\nКак я могу к Вам обращаться?'
        update._effective_message.reply_chat_action(action='Typing',timeout=200)
        update.message.reply_text(reply_text,reply_markup=ReplyKeyboardRemove())
        context.bot.send_message(chat_id=TELEGRAM_SUPPORT_CHAT_ID,text='Connected {user_info}')
        return WELCOME
    else:
        msg = 'Привет , чтобы ответить на вопрос клиента, ответь на запрос который я отправляю'
        update.message.reply_text(msg)


def tickets(update:Update, context:CallbackContext):
    if update.message.chat.type != 'private':
        ticket_text='Тут будут тикеты'
        update.message.reply_text(ticket_text)
    else:
        pass

def welcome(update,context):
    text = update.message.text
    reply_text = f'Рад Вас приветствовать {text}!\nЧем я могу вам помочь?'
    update.message.reply_text(reply_text, reply_markup=menu)

    return CHOISE_CREDIT_OR_EAT


def eat(update:Update,context:CallbackContext):
    eat_text = 'По программе «Субсидирование доставки еды» Вы можете возместить уплаченную комиссию агрегаторам по доставке продуктов и еды.\nК сожалению, программа пока не запущена'
    update.message.reply_text(eat_text,reply_markup=info_for_start_program)

    return HAVE_QUESTION

def credit(update:Update,context:CallbackContext):
    credit_text = 'По программе «Субсидирование процентной ставки»\nВы можете возместить уплаченные проценты за период с 01.01.2020 по действующим кредитам.\nК сожалению, программа пока не запущена'
    update.message.reply_text(credit_text,reply_markup=info_for_start_program)

    return HAVE_QUESTION

def any_question(update:Update,context:CallbackContext):
    get_new_keyboard = 'Воспользуйтесь кнопками ниже,чтобы задать вопрос нашим сотрудникам, просто напишите текст'
    update.message.reply_text(get_new_keyboard,reply_markup=question_keyboard)
    return CHOSING





#(User - Support Chat)
def get_question(update:Update, context:CallbackContext):
    if update.message.chat.type == 'private':
        text = update.message.text
        update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)
    else: pass

    return CHOSING

#(Suport Chat- User)
def forward_to_user(update:Update, context:CallbackContext):


    user_ud = update.message.reply_to_message.forward_from.id
    context.bot.send_message(chat_id=user_ud,text=update.message.text)

    return forward_to_user


def notification(update:Update,context:CallbackContext):
    reply_text = "Как только мы откроем прием заявок – Вам придет уведомление!"
    update.message.reply_text(reply_text,reply_markup=ReplyKeyboardRemove())
    return ConversationHandler.END

def cancel(update,context) -> int:
    user = update.message.from_user
    logging.info("User %s canceled the conversation.", user.first_name)
    update.message.reply_text(
        'Bye! I hope we can talk again some day.', reply_markup=ReplyKeyboardRemove()
    )
    return ConversationHandler.END


def main() ->None:
    updater = Updater(TELEGRAM_TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('tickets',tickets))
    conv_handler = ConversationHandler(
    entry_points=[CommandHandler('start',start)],
    states={
        WELCOME:[
            MessageHandler(
                Filters.text & ~Filters.command,welcome
            )
        ],
        CHOISE_CREDIT_OR_EAT:[
            MessageHandler(
                Filters.regex('^Хочу возместить проценты по кредиту$'),credit
            ),
            MessageHandler(Filters.regex('^Хочу возместить комиссию за доставку$'),eat),
        ],
        HAVE_QUESTION:[
            MessageHandler(
                Filters.regex('^У ведомить меня о старте программы$'),notification
            ),
            MessageHandler(
              Filters.regex('^У меня остались вопросы$'),any_question),
        ],
        CHOSING:[
            MessageHandler(
                Filters.text,get_question
            ),
            MessageHandler(
               Filters.chat(TELEGRAM_SUPPORT_CHAT_ID) & Filters.reply, forward_to_user
            ),
        ],
        TO_USER:[
            MessageHandler(
                Filters.chat(TELEGRAM_SUPPORT_CHAT_ID)&Filters.reply,forward_to_user
            ),
        ],
    },
    fallbacks=[CommandHandler('cancel',cancel)],
    )
    dispatcher.add_handler(conv_handler)
    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()


"""
def forward_to_chat(update, context):
  
    update.message.forward(chat_id=TELEGRAM_SUPPORT_CHAT_ID)


def forward_to_user(update, context):

    user_id = update.message.reply_to_message.forward_from.id
    context.bot.copy_message(
        message_id=update.message.message_id,
        chat_id=user_id,
        from_chat_id=update.message.chat_id
    )

"""
"""


    """
