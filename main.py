import hashlib
import hmac
import json
import time

import openai

import aiogram.types
import requests
from aiogram import types
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from aiogram.utils import executor
from aiogram.utils.deep_linking import get_start_link

import markups
from config import dp, bot, db, secretKey
from states import Admin

dialog_states = {}


# Обращение к API
async def chat(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2040,
        n=1,
        stop=None,
        temperature=0,
    ).choices[0].text
    return response


async def process_ref_args(user_id: int, inviter_id):
    if inviter_id != '':
        try:
            inviter_id = int(inviter_id)
        except:
            return
        if (inviter_id != user_id) and not (str(user_id) in db.get_invited_users(inviter_id)) and not (
                db.user_exists(user_id)):
            db.add_user(user_id)

            db.set_inviter_id(user_id=user_id, inviter_id=inviter_id)
            db.update_invited_users(user_id, inviter_id)


async def finish_dialog(user_id, username):
    admin_id = open("admin_id.txt", "r", encoding="utf-8").read()
    if user_id == admin_id:
        text = f"Диалог c @{username} завершен✅"
    else:
        text = f"Диалог завершен✅"
    await bot.send_message(user_id, text, reply_markup=markups.get_main_keyb(user_id))


@dp.message_handler(commands=['start'])
async def reply_menu(msg: types.Message):
    print(msg.from_user.id)
    args = msg.get_args()
    await process_ref_args(user_id=msg.from_user.id, inviter_id=args)

    db.add_user(msg.from_user.id) if not db.user_exists(msg.from_user.id) else None
    await bot.send_message(msg.from_user.id,
                           """Просто напишіть на будь-якій мові питання до штучного інтелекту 💬 і отримайте 
                           відповідь 😎""",
                           reply_markup=markups.get_main_keyb(msg.from_user.id))


@dp.message_handler(content_types=['text'], state=Admin.support_dialog)
async def get_user_problem(msg: types.Message, state: FSMContext):
    admin_id = open("admin_id.txt", "r", encoding="utf-8").read()
    print(admin_id)
    with open(f"dialogs.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    if msg.text == "Завершить диалог":
        await state.finish()
        try:
            for st in dialog_states[int(data.get("user_id"))]:
                try:
                    await st.finish()
                except Exception as e:
                    continue
        except:
            pass

        user_id = json.load(open("dialogs.json", 'r', encoding="utf-8")).get("user_id")
        uids = [user_id if user_id is not None else msg.from_user.id, admin_id]

        uids.remove(admin_id) if data.get("user_id") is None else None
        username = "None" if json.load(open("dialogs.json", 'r', encoding="utf-8")).get(
            "uname") is None else json.load(open("dialogs.json", 'r', encoding="utf-8")).get("uname")

        for uid in uids:
            await finish_dialog(user_id=uid, username=username)

        try:
            dialog_states[int(data.get("user_id"))].clear()
        except TypeError:
            pass
        with open("dialogs.json", "w", encoding="utf-8") as f:
            json.dump({}, f, indent=4, ensure_ascii=False)
    else:
        if str(msg.from_user.id) == admin_id:
            user_id = int(data["user_id"])
            dialog_states[user_id].append(state) if len(dialog_states[user_id]) == 1 else None

            print(dialog_states, "after admin answer")
            await bot.send_message(user_id, msg.text)
        else:
            if data.get("user_id") is None:
                await bot.send_message(admin_id, f"У юзера @{msg.from_user.username} проблема:\n"
                                                 f"{msg.text}", reply_markup=InlineKeyboardMarkup(
                    inline_keyboard=[
                        [InlineKeyboardButton(text="Начать диалог",
                                              callback_data=f"start_dialog_with_user-{msg.from_user.id}")]
                    ]
                ))

                data = {"user_id": msg.from_user.id,
                        "uname": msg.from_user.username if msg.from_user.username is not None else "None",
                        "problem": msg.text}
                with open("dialogs.json", "w", encoding="utf-8") as f2:
                    json.dump(data, f2, indent=4, ensure_ascii=False)

                dialog_states[int(data.get("user_id"))] = [state]
                print(dialog_states, "before admin answer")
                await bot.send_message(msg.from_user.id,
                                       "Сообщение направлено. Ожидайте, поддержка скоро с вами свяжется")
            else:
                if data.get("accepted_dialog") is True:
                    await bot.send_message(admin_id, f"{msg.text}")


@dp.callback_query_handler(Text(startswith="start_dialog_with_user"))
async def start_dialog_with_user(call: types.CallbackQuery):
    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, "Вы начали диалог", reply_markup=ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Завершить диалог")],
        ],
        resize_keyboard=True,
        row_width=2
    ))
    with open("dialogs.json", "r", encoding="utf-8") as f:
        data = json.load(f)
        data["accepted_dialog"] = True

        data["user_id"] = call.data.split("-")[1]
        with open("dialogs.json", 'w', encoding="utf-8") as fw:
            json.dump(data, fw, indent=4, ensure_ascii=False)
        await bot.send_message(data["user_id"], "Поддержка начала с вами диалог")
    await Admin.support_dialog.set()


@dp.callback_query_handler(Text(startswith="buy"))
async def buy_product(call: types.CallbackQuery):
    category, index = call.data.split('-')[1:]
    product_to_buy = db.get_products_by_category(category)[int(index)]

    order_time = int(time.time())

    name, description, price = product_to_buy[2:]
    merchantAccount, merchantDomainName, orderReference, amount, currency, orderDate = "prolink_biz", "https://t.me/kapteka_shop_bot", f"kapteka_order-{product_to_buy[0]}{'-@' + call.from_user.username if call.from_user.username is not None else ''}-{call.from_user.id}-{order_time}-{call.message.message_id}", str(price), open(
        "currency.txt", "r", encoding="utf-8").read(), int(
        time.time())

    merchantSignature = hmac.new(secretKey, ';'.join(
        [merchantAccount, merchantDomainName, orderReference, str(orderDate), amount, currency, name, "1",
         str(price)]).encode("utf-8"), hashlib.md5).hexdigest()

    service_url = "http://185.233.116.97:8003/"
    pay_data = {
        "transactionType": "CREATE_INVOICE",
        "merchantAccount": merchantAccount,
        "merchantAuthType": "SimpleSignature",
        "merchantDomainName": merchantDomainName,
        "merchantSignature": merchantSignature,
        "apiVersion": 1,
        "language": "ru",
        "serviceUrl": service_url,
        "orderReference": orderReference,
        "orderDate": orderDate,
        "amount": amount,
        "currency": currency,
        "orderTimeout": 86400,
        "productName": [name],
        "productPrice": [int(price)],
        "productCount": [1],
        "paymentSystems": "card",
        "clientFirstName": str(call.from_user.first_name),
        "clientLastName": str(call.from_user.last_name) if call.from_user.last_name is not None else "Aki",
    }
    invoice_url = requests.post(url="https://api.wayforpay.com/api", json=pay_data).json()["invoiceUrl"]

    await bot.delete_message(call.from_user.id, call.message.message_id)
    await bot.send_message(call.from_user.id, f"Нажмите оплатить для перехода на страницу оплаты",
                           reply_markup=InlineKeyboardMarkup(
                               inline_keyboard=[
                                   [InlineKeyboardButton(text="Оплатить", url=invoice_url)]
                               ]
                           ))


# Обработка сообщений
@dp.message_handler(content_types=['text'])
async def handle_text(msg: aiogram.types.Message):
    with open("admin_id.txt", "r") as f:
        admin_id = int(f.read())
    if msg.text == "📲 Підтримка":
        if msg.from_user.id != admin_id:
            await bot.delete_message(msg.from_user.id, msg.message_id)
            await bot.send_message(msg.from_user.id, "Надішліть сюди вашу проблему", reply_markup=ReplyKeyboardMarkup(
                keyboard=[
                    [KeyboardButton(text="Завершити діалог")]
                ],
                resize_keyboard=True,
                row_width=2
            ))
            with open("dialogs.json", "w", encoding="utf-8") as f:
                json.dump({}, f, indent=4, ensure_ascii=False)

            await Admin.support_dialog.set()
        else:
            await bot.send_message(msg.from_user.id, "Поддержка не может написать самой себе)")

    elif msg.text == "💰 Реферальна програма":
        await bot.send_message(msg.from_user.id,
                               f"Пригласите своих друзей в бота по реферальной ссылке и получайте процент с их покупок!\n"
                               f"Ваша реферальная ссылка:\n"
                               f"`{await get_start_link(payload=msg.from_user.id)}`\n\n"
                               f"Пользователей приглашено: {len(db.get_invited_users(msg.from_user.id).split())}\n"
                               f"Текущий процент с покупок: 10", parse_mode="MARKDOWN")
    elif msg.text == "Сделать рассылку":
        if msg.from_user.id == admin_id:
            await bot.send_message(admin_id, "Отправьте сообщение, которое разошлется всем пользователям",
                                   reply_markup=markups.break_load_process_keyboard)
            await Admin.make_newsletter.set()
    else:
        if db.user_has_sub_or_test_period(user_id=msg.from_user.id):
            await bot.send_message(msg.from_user.id, 'Я пишу вам відповідь, трошки зачекайте 😇')
            response = await chat(msg.text)

            if len(response) > 4096:
                response1 = response[:4096]
                response2 = response[4096:]
                await bot.send_message(chat_id=msg.chat.id, text=response1, reply_to_message_id=msg.message_id)
                await bot.send_message(chat_id=msg.chat.id, text=response2, reply_to_message_id=msg.message_id)

            else:
                await bot.send_message(
                    chat_id=msg.from_user.id,
                    text=str(response).strip(),
                    reply_to_message_id=msg.message_id,
                    parse_mode=types.ParseMode.MARKDOWN
                )
        else:
            await bot.send_message(msg.from_user.id, "Тестовий перiод закiнчився, отримайте необмежений доступ на місяць всього за 5$\n"
                                                     "Зверніться у Підтримку 📲")

if __name__ == '__main__':
    # Start polling
    executor.start_polling(dp, skip_updates=True)
