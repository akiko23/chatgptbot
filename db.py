import random
import sqlite3
import string
import time


class Database:
    def __init__(self, db_file):
        self.connection = sqlite3.connect(db_file, check_same_thread=False)
        self.cursor = self.connection.cursor()

    def request_to_database(self, request, *args):
        with self.connection:
            return self.cursor.execute(request, *args)

    def add_user(self, user_id):
        time_now = int(time.time())
        self.request_to_database("INSERT INTO bot_user (user_id, money, registration_date, has_sub) VALUES (?, 0, ?, FALSE)", (user_id, time_now))

    def user_exists(self, user_id):
        res = self.request_to_database("SELECT `user_id` FROM bot_user WHERE user_id=?", (user_id,)).fetchall()
        return bool(len(res))

    def set_inviter_id(self, user_id, inviter_id):
        self.request_to_database("UPDATE bot_user SET inviter_id=? WHERE user_id=?", (inviter_id, user_id,))

    def get_invited_users(self, user_id):
        try:
            return \
                self.request_to_database("SELECT invited_users FROM bot_user WHERE user_id=?", (user_id,)).fetchall()[
                    0][
                    0].strip()
        except AttributeError:
            return ''

    def get_user_purchases(self, user_id):
        try:
            return self.request_to_database("SELECT purchases FROM bot_user WHERE user_id=?", (user_id,)).fetchall()[0][
                0].strip()
        except AttributeError:
            return ''

    def update_invited_users(self, user_id, inviter_id):
        invited_users = self.get_invited_users(inviter_id).split()
        invited_users.append(str(user_id))

        self.request_to_database("UPDATE bot_user SET invited_users=? WHERE user_id=?",
                                 (" ".join(invited_users), inviter_id,))

    def get_ref_percent(self):
        return self.request_to_database("SELECT percent FROM bot_refpercent").fetchone()[0]

    def set_purchase(self, order_reference):
        try:
            product_id, uname, user_id, order_time, msg_id = order_reference.split("-")[1:]
        except:
            product_id, user_id, order_time, msg_id = order_reference.split("-")[1:]
        user_purchases = self.get_user_purchases(user_id).split()
        user_purchases.append(order_reference)

        return self.request_to_database("UPDATE bot_user SET purchases=? WHERE user_id=?",
                                        (" ".join(list(set(user_purchases))), user_id,))

    def get_all_users(self):
        return [i[0] for i in self.request_to_database("SELECT user_id FROM bot_user").fetchall()]

    def get_reg_date(self, user_id):
        return self.request_to_database("SELECT registration_date From bot_user WHERE user_id=?", (user_id,)).fetchone()[0]

    def user_has_sub(self, user_id):
        return self.request_to_database("SELECT has_sub From bot_user WHERE user_id=?", (user_id,)).fetchone()[0]

    def user_has_sub_or_test_period(self, user_id):
        reg_date = self.get_reg_date(user_id)
        return self.user_has_sub(user_id) or int(time.time()) - int(reg_date) <= 86400


# db = Database('db.sqlite3')
# print(db.get_all_users())
