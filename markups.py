import random

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton

from config import db


def product_menu(category):
    advertisement_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Добавить товар', callback_data=f'product_add_{category}'),
                InlineKeyboardButton('Смотреть товары', callback_data=f'product_watchall_{category}'),
            ],
            [
                InlineKeyboardButton('Назад', callback_data='show_categories')
            ]
        ]
    )
    return advertisement_keyboard


def get_main_keyb(user_id):
    admin_id = open("admin_id.txt", "r", encoding="utf-8").read()
    main_keyb = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="📲 Підтримка")],
            [KeyboardButton(text="💰 Реферальна програма")],
        ],
        resize_keyboard=True,
        row_width=3
    )

    main_keyb.keyboard[-1].append(KeyboardButton(text="Сделать рассылку")) if admin_id == str(user_id) else None
    return main_keyb


def actions_with_advertisement(unique_id):
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Изменить', callback_data=f'advertisement_change-{unique_id}'),
                InlineKeyboardButton('Удалить', callback_data='advertisement_delete'),

            ],
            [
                InlineKeyboardButton('Назад', callback_data='back-to_user_advertisements')
            ]
        ]
    )
    return keyboard


def choose_param_to_change():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton('Фото', callback_data='change-photo'),
                InlineKeyboardButton('Название', callback_data='change-name'),
                InlineKeyboardButton('Описание', callback_data='change-description'),
                InlineKeyboardButton('Цену', callback_data='change-price')
            ],

            [
                InlineKeyboardButton('Назад', callback_data='back-to_user_advertisement')
            ]
        ],

    )
    return keyboard


break_load_process_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Отмена', callback_data='break_load_process')
        ]
    ]
)

break_changing_process_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text='Отмена', callback_data='break_change_process')
        ]
    ]
)


def set_menu_on_watching(all_ads_len, current_num, category):
    inline_obj = []
    if (current_num == all_ads_len - 1) and all_ads_len != 1:
        inline_obj = [InlineKeyboardButton('Предыдущее', callback_data=f'watchpr-prev-{current_num}-{category}')]
    elif current_num == 0:
        inline_obj = [InlineKeyboardButton('Следующее', callback_data=f'watchpr-next-{current_num}-{category}')]
    if 0 < current_num < all_ads_len - 1:
        inline_obj = [InlineKeyboardButton('Предыдущее', callback_data=f'watchpr-prev-{current_num}-{category}'),
                      InlineKeyboardButton('Следующее', callback_data=f'watchpr-next-{current_num}-{category}')]
    if all_ads_len == 1:
        inline_obj = []
    return InlineKeyboardMarkup(
        inline_keyboard=
        [
            inline_obj,
            [InlineKeyboardButton(text="Купить", callback_data=f"buy-{category}-{current_num}")],
        ]
    )


def get_category_keyb(uid):
    keyb = InlineKeyboardMarkup()
    categories = list(db.get_all_categories())

    c = 0
    for i in range(len(categories)):
        add_success = 0
        try:
            keyb.inline_keyboard.append(
                [InlineKeyboardButton(text=categories[c], callback_data=f"cat-{categories[c]}")]
            )
        except IndexError:
            break
        try:
            keyb.inline_keyboard[c - random.randint(1, len(categories) - len(categories) // 2)].append(
                InlineKeyboardButton(text=categories[c + 1], callback_data=f"cat-{categories[c + 1]}")
            )
            add_success = 1
        except IndexError:
            pass
        c += sum([1, add_success])

    if uid in [137506556]:
        keyb.inline_keyboard.append([InlineKeyboardButton(text="Добавить категорию", callback_data="add_category")])
    return keyb


def on_choose_advertisement(user_advertisements):
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text=ad[4], callback_data=f"useradvertisement_{ad[0]}")
                for ad in user_advertisements
            ],
            [
                InlineKeyboardButton('Вернуться в главное меню', callback_data='back-to_advertisement_menu')
            ]
        ]
    )


def watch_all_advertisements_options():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text='Поиск по названию', callback_data='all_advertisements-search'),
                InlineKeyboardButton(text='Смотреть все', callback_data='all_advertisements-watch')
            ],
            [
                InlineKeyboardButton('Вернуться в главное меню', callback_data='back-to_advertisement_menu')
            ]
        ]
    )
