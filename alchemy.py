from sqlalchemy import Column
from sqlalchemy import Integer, String, DateTime
from sqlalchemy import create_engine
from sqlalchemy import ForeignKey
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


Base = declarative_base()
engine = create_engine('mysql+mysqlconnector://root:Stavstat12@127.0.0.1:3306/ga2')


class Admins(Base):
    __tablename__ = 'admins'
    id = Column(Integer, primary_key=True)
    t_id = Column(Integer)
    name = Column(String(50))

    def __init__(self, t_id, name):
        self.t_id = t_id
        self.name = name


class Gameplay(Base):
    __tablename__ = 'gameplay'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    chat_id = Column(Integer)
    level = Column(Integer)

    def __init__(self, game_id, chat_id, level):
        self.game_id = game_id
        self.chat_id = chat_id
        self.level = level


class Levels(Base):
    __tablename__ = 'levels'
    id = Column(Integer, primary_key=True)
    game_id = Column(Integer)
    sn = Column(Integer)
    header = Column(String(50))
    task = Column(String(50))
    answer = Column(String(50))
    tip = Column(String(50))

    def __init__(self, game_id, sn, header, task, answer, tip):
        self.game_id = game_id
        self.sn = sn
        self.header = header
        self.task = task
        self.answer = answer
        self.tip = tip


class Games(Base):
    __tablename__ = 'games'
    id = Column(Integer, primary_key=True)
    name = Column(String(50))
    descrition = Column(String(150))
    number_of_levels = Column(Integer)
    date = Column(DateTime)
    owner = Column(Integer)
    code = Column(String(50))
    #sequence = Column(String(50))

    def __init__(self, name, description, number_of_levels, date, owner, code):
        self.name = name
        self.descrition = description
        self.number_of_levels = number_of_levels
        self.date = date
        self.owner = owner
        self.code = code
        #self.sequence = sequence


Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)                           # Инициализация сессии
session = Session()

#session.add(Admins(235987482, 'beeline'))
#session.add(Games('ggg', 'ggg', 5, '2018-05-24 16:00:00', 235987482, 'IUP8W7'))



session.commit()                                              # Запись в БД

#for i in session.query(Admins.id):
#    print(i.id)

#if i in session.query(Admins.id):
#    print('yes')

#print(list(session.query(Admins.id)))

#result = list(map(lambda x: x[0], session.query(Admins.id)))
#print(result)