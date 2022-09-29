from matplotlib import pyplot as plt
from PIL import Image


class case():
    def __init__(self, id):
        self.user_id = id
        self.fotos = []
        self.gps = None
        self.comment = ''
        self.carrent = None
        self.questions = {
            'кто это был?\n(если неуверен выбери несколько))':
            ['мент', 'военком', 'дпс', 'жилищник', 'другой'],
            'где это было?\n(если неуверен выбери несколько)': [
                'на работе', 'в метро', 'на улице у метро',
                'на автобусной остановке', 'на дороге', 'во дворе',
                'у офисного здания', 'у квартиры'
            ]
        }
        self.question = iter(self.questions.items())
        self.answer = {}

    def __del__(self):
        'send all data to mango'
        print('gps', self.gps)
        print('commet', self.comment)
        print(self.answer)
        for foto in self.fotos:
            img = Image.open(foto)
            img.show()

    def add_foto(self, foto):
        self.fotos += [foto]
        self.carrent = 'фото'

    def add_comment(self, comment):
        if len(self.comment) > 0:
            self.comment = self.comment + '\n\n' + comment
        else:
            self.comment = comment
        self.carrent = 'комментарий'

    def add_gps(self, latitude, longitude):
        self.gps = (latitude, longitude)
        self.carrent = 'геолокация'

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
