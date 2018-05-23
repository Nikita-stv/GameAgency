from sqlalchemy import MetaData
from sqlalchemy import Table, Column
from sqlalchemy import Integer, String, Numeric, DateTime, Enum
from sqlalchemy import create_engine, select
from sqlalchemy import ForeignKey
from sqlalchemy import Unicode, UnicodeText
from sqlalchemy import ForeignKeyConstraint
from sqlalchemy import inspect
from sqlalchemy.dialects import mysql


class Alchemy:

    def __init__(self):
        self.metadata = MetaData()

        self.admins = Table('admins', self.metadata,
                           Column('id', Integer, primary_key=True),
                           Column('telegram_id', Integer),
                           Column('name', String(50))
                           )

        self.gameplay = Table('gameplay', self.metadata,
                                Column('game_id', Integer, ForeignKey('list_of_games.id')),
                                Column('chat_id', Integer),
                                Column('level', Integer)
                                )

        self.levels = Table('levels', self.metadata,
                       Column('id', Integer, primary_key=True),
                       Column('game_id', Integer),
                       Column('sn', Integer),
                       Column('header', String(50)),
                       Column('task', String(50)),
                       Column('answer', String(50)),
                       Column('tip', String(50))
                       )

        self.list_of_games = Table('list_of_games', self.metadata,
                              Column('id', Integer, primary_key=True),
                              Column('name', String(50)),
                              Column('description', String(50)),
                              Column('number_of_levels', Integer),
                              Column('date', DateTime),
                              Column('owner', Integer),
                              Column('code', String(6)),
                              Column('sequence', String(50))
                              )


        self.engine = create_engine('mysql+mysqlconnector://root:Stavstat12@127.0.0.1:3306/ga2')
        self.metadata.create_all(self.engine)
        conn = self.engine.connect()

    # INSERT
    def insert_game(self, game):
        conn = self.engine.connect()
        print(game)
        conn.execute(self.list_of_games.insert().values(name=game[1],description=game[2], number_of_levels=game[3],date=game[4],owner=game[5], code=game[6]))
        #conn.execute(self.list_of_games.insert(), [ {'username': 'jack', 'fullname': 'Jack Burger'}, {'username': 'wendy', 'fullname': 'Wendy Weathersmith'}])

    def insert_levels(self, game_id, lev):
        conn = self.engine.connect()
        param = []
        for i in range(lev):
            param.append({'game_id':game_id, 'sn':i+1})
        conn.execute(self.levels.insert(), param)


    # SELECT
    def select_admin(self):
        conn = self.engine.connect()
        adm = conn.execute(select([self.admins.c.telegram_id])).fetchall()
        result = []
        for row in adm:
            result.append(row[0])
        return result

#print(str(Alchemy.select()))
#Alchemy().select()