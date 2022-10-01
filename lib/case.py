from PIL import Image
import os
import pymongo
from bson.objectid import ObjectId
import gridfs
import time
import datetime
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import dotenv

db = None
fs = None
users = None


def connect_to_mongo():
    global db, fs, users
    dotenv.load_dotenv('keys/keys.env')
    client = pymongo.MongoClient(host=os.environ['host'],
                                 port=int(os.environ['port']),
                                 replicaSet='rs01',
                                 username=os.environ['username'],
                                 password=os.environ['password'],
                                 authSource=os.environ['database'],
                                 tls=True,
                                 tlsCAFile='keys/cert.pem')
    db = client[os.environ['database']]
    fs = gridfs.GridFS(db)
    users = db['users']


def add_user(id, **args):
    data = dict(args)
    if users.find_one({'_id': id}) is None:
        data['_id'] = id
        data['cases'] = []
        users.insert_one(data)
        print(id)
    else:
        users.update_one({'_id': id}, {'$set': data})


class case():
    def __init__(self, id):
        self.user_id = id
        self.fotos = []
        self.gps = None
        self.comment = ''
        self.carrent = None
        self.time = {'gps': [], 'foto': [], 'comment': [], 'answers': []}
        self.question_text = {
            'who': 'кто это был?\n(если неуверен выбери несколько)',
            'where': 'где это было?\n(если неуверен выбери несколько)',
            'when': 'как давно это было?\nвыбери самое близкое время'
        }
        self.questions = {
            'who': ['мент', 'военком', 'дпс', 'жилищник', 'другой'],
            'where': [
                'на работе', 'в метро', 'на улице у метро',
                'на автобусной остановке', 'на дороге', 'во дворе',
                'у офисного здания', 'у квартиры'
            ],
            'when': [
                'сейчас', '10 мин назад', 'полчаса назад', 'час назад',
                '2 часа назад', '4 часа назад', '8 часов назад', 'вчера'
            ]
        }
        self.question_patam = {
            'who': {
                'allows_multiple_answers': True
            },
            'where': {
                'allows_multiple_answers': True
            },
            'when': {
                'allows_multiple_answers': False
            }
        }
        self.carrent_que = None
        self.question = iter(self._gen_quetion())
        self.answers = {}
        

    def __del__(self):
        'send all data to mango'
        tmin = float('+inf')
        for t_arr in self.time.values():
            for t in t_arr:
                tmin = min(tmin, t)
        tmax = float('-inf')
        for t_arr in self.time.values():
            for t in t_arr:
                tmax = max(tmax, t)
        if tmin == float('+inf'):
            return

        self.time['median'] = (tmin + tmax) / 2
        self.time['dt'] = tmax - tmin
        self.save_case()

        print('gps', self.gps)
        print('commet', self.comment)
        print(self.answers)
        print(self.user_id)
        print(datetime.datetime.fromtimestamp(self.time['median']))
        print(self.time['dt'])
        print(self.time)
        for foto in self.fotos:
            img = Image.open(foto)
            img.show()

    def save_case(self):
        foto_ids = []
        for foto in self.fotos:
            foto_ids.append(fs.put(foto))
        doc = {
            'gps': self.gps,
            'foto': foto_ids,
            'comment': self.comment,
            'answers': self.answers,
            'question': self.questions,
            'time': self.time,
            'user': self.user_id
        }
        resalt = db['cases'].insert_one(doc)
        id = resalt.inserted_id
        print(id)
        users.update_one({'_id': self.user_id}, {'$push': {'cases': id}})
        print(users.find_one({'_id': self.user_id})['cases'])
        print('resalts saved to db')

    def add_foto(self, foto):
        self.time['foto'].append(time.time())
        self.fotos += [foto]
        self.carrent = 'фото'

    def add_comment(self, comment):
        self.time['comment'].append(time.time())
        if len(self.comment) > 0:
            self.comment = self.comment + '\n\n' + comment
        else:
            self.comment = comment
        self.carrent = 'комментарий'

    def add_gps(self, latitude, longitude):
        self.time['gps'].append(time.time())
        self.gps = (latitude, longitude)
        self.carrent = 'геолокация'

    def add_ans(self, ans):
        self.time['answers'].append(time.time())
        self.answers[self.carrent_que] = ans

    def _gen_quetion(self):
        for que, ans in self.questions.items():
            self.carrent_que = que
            yield self.question_text[que], ans, self.question_patam[que]

    @property
    def open_position(self):
        resalt = []
        if self.gps is None:
            resalt += ['геолокация']
        if len(self.fotos) == 0:
            resalt += ['фото']
        if self.comment == '':
            resalt += ['комментарий']
        return resalt

    if __name__ == '__main__':
        print(db)
        connect_to_mongo()
        print(db)
        add_user(id=33432424, qwer=5, fhfh='eer')