import sqlite3


class DataBase:
    def __init__(self, name='users.db'):
        self.conn = sqlite3.connect(name)

    def __enter__(self):
        self.__setup()
        return self

    def __exit__(self, error_type, value, traceback):
        self.close()

    def __setup(self):
        self.conn.execute(
            'CREATE TABLE IF NOT EXISTS users ('
            'user_id INTEGER PRIMARY KEY UNIQUE,'
            'language TEXT DEFAULT "en",'
            'favourite TEXT,'
            'requests INTEGER DEFAULT 0)'
        )
        self.conn.commit()

    def __make_request(self, query, args=tuple()):
        self.conn.execute(query, args)
        self.conn.commit()

    def __fetch_data(self, query, args=tuple()):
        if result := self.conn.execute(query, args).fetchone():
            return result[0]

    def close(self):
        self.conn.close()

    def add_user(self, user_id):
        if not self.if_users_exists(user_id):
            self.__make_request('INSERT INTO users (user_id) VALUES (?)', (user_id, ))

    def del_user(self, user_id):
        if self.if_users_exists(user_id):
            self.__make_request('DELETE FROM users WHERE user_id = (?)', (user_id, ))

    def if_users_exists(self, user_id):
        return self.__fetch_data('SELECT EXISTS(SELECT 1 FROM users WHERE user_id = (?))', (user_id, ))

    def get_users_amount(self):
        return self.__fetch_data('SELECT Count(*) FROM users')

    def get_requests_amount(self):
        return self.__fetch_data('SELECT SUM(requests) FROM users')

    def set_language(self, user_id, data):
        if self.if_users_exists(user_id):
            self.__make_request('UPDATE users SET language = (?) WHERE user_id = (?)', (data, user_id))

    def get_language(self, user_id):
        return self.__fetch_data('SELECT language FROM users WHERE user_id = (?)', (user_id, ))

    def set_requests(self, user_id, data):
        if self.if_users_exists(user_id):
            self.__make_request('UPDATE users SET requests = (?) WHERE user_id = (?)', (data, user_id))

    def get_requests(self, user_id):
        return self.__fetch_data('SELECT requests FROM users WHERE user_id = (?)', (user_id, ))

    def set_favourite(self, user_id, data):
        if self.if_users_exists(user_id):
            self.__make_request('UPDATE users SET favourite = (?) WHERE user_id = (?)', (data, user_id))

    def get_favourite(self, user_id):
        return self.__fetch_data('SELECT favourite FROM users WHERE user_id = (?)', (user_id, ))
