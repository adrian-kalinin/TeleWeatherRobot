import sqlite3


class DBHelper:
    def __init__(self, name='userdata.sqlite'):
        self.name = name
        self.conn = sqlite3.connect(name)

    def __enter__(self):
        self.setup()
        return self

    def __exit__(self, type, value, traceback):
        self.close()

    def setup(self):
        self.conn.execute('CREATE TABLE IF NOT EXISTS userdata ('
                          'user_id INTEGER NOT NULL PRIMARY KEY UNIQUE,'
                          'lang TEXT NOT NULL DEFAULT "en",'
                          'favourite TEXT,'
                          'stat INTEGER NOT NULL DEFAULT 0);')
        self.conn.commit()

    def get_users(self):
        return [x[0] for x in self.conn.execute('SELECT user_id FROM userdata')]

    def add_user(self, user_id):
        if not self.check_user(user_id):
            stat = 'INSERT INTO userdata (user_id) VALUES (?)'
            args = (user_id,)
            self.conn.execute(stat, args)
            self.conn.commit()

    def del_user(self, user_id):
        self.add_user(user_id)

        stat = 'DELETE FROM userdata WHERE user_id = (?)'
        args = (user_id,)
        if self.check_user(user_id):
            self.conn.execute(stat, args)
            self.conn.commit()

    def check_user(self, user_id):
        stat = 'SELECT user_id FROM userdata WHERE user_id = (?)'
        args = (user_id,)
        if len([x[0] for x in self.conn.execute(stat, args)]):
            return True

    def get_amount_of_users(self):
        stat = 'SELECT Count(*) FROM userdata'
        result = self.conn.execute(stat)
        return result.fetchone()[0]

    def get_total_amount_stat(self):
        stat = 'SELECT SUM(stat) FROM userdata'
        result = self.conn.execute(stat)
        return result.fetchone()[0]

    def set(self, user_id, item, data):
        self.add_user(user_id)

        stat = f'UPDATE userdata SET {item} = (?) WHERE user_id = (?)'
        self.conn.execute(stat, (data, user_id))
        self.conn.commit()

    def get(self, user_id, item):
        self.add_user(user_id)

        stat = f'SELECT {item} FROM userdata WHERE user_id = (?)'
        result = self.conn.execute(stat, (user_id,)).fetchone()
        if result:
            return result[0]

    def close(self):
        self.conn.close()
