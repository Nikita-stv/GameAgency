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
                              Column('owner', Integer, ForeignKey('admins.telegram_id')),
                              Column('code', String(6)),
                              Column('sequence', String(50))
                              )


        engine = create_engine('mysql+mysqlconnector://root:Stavstat12@127.0.0.1:3306/ga2')
        self.metadata.create_all(engine)
        self.conn = engine.connect()

    # INSERT
    #insert_stmt = admins.insert().values(telegram_id='235987482', name='Beeline')
    #conn = engine.connect()
    #result = conn.execute(insert_stmt)

    # SELECT
    def select(self):
        select_admin = select([self.admins.c.telegram_id])
        adm = self.conn.execute(select_admin).fetchall()
        result = []
        for row in adm:
            result.append(row[0])
        return result

#print(str(Alchemy.select()))
#Alchemy().select()