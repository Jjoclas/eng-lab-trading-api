import time
import logging
import json
from iqoptionapi.stable_api import IQ_Option
from decouple import config

logging.disable(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)


class IqOption:
    API = IQ_Option(config('IQEMAIL'), config('IQPASS'))
    balance_type: str = 'TOURNAMENT' # PRACTICE / REAL / TOURNAMENT

    def __init__(self, balance='PRACTICE'):
        self.balance_type = balance
        self.API.connect()
        if self.API.check_connect() == False:
            logging.info('Erro ao se conectar')
        else:
            logging.info('Conectado com sucesso')


    def change_balance(self, type: str=None):
        if not type:
            type = self.balance_type

        self.API.change_balance(type) 
        logging.info(f'Balance Type: {self.balance_type}')


    def perfil(self): # Função para capturar informações do perfil
        perfil = json.loads(json.dumps(self.API.get_profile_ansyc()))
        '''
            name
            first_name
            last_name
            email
            city
            nickname
            currency
            currency_char 
            address
            created
            postal_index
            gender
            birthdate
            balance		
        '''
        return perfil

    def get_realtime_candles(self, str_moeda: str='EURUSD', num_intervalo: int=60, qtd: int=1):
        self.API.start_candles_stream(str_moeda, num_intervalo, qtd)
        dict_candles: list = self.API.get_realtime_candles(str_moeda, num_intervalo)
        self.API.stop_candles_stream(str_moeda, num_intervalo)
        return dict_candles.values()

    def get_candles(self, num_quantidade, str_moeda='EURUSD', num_intervalo=1, tempo=time.time()):
        import math
        list_velas = []

        num_range = math.ceil(num_quantidade / 1000)
        num_intervalo = num_intervalo * 60
        for i in range(num_range):
            num_candles = num_quantidade if num_quantidade < 1000 else 1000
            list_sub_velas = self.API.get_candles(str_moeda, num_intervalo, num_candles, tempo)
            list_velas.extend(list_sub_velas)
            try:
                tempo = int(list_sub_velas[0]['from'])-1
                num_quantidade -= 1000
            except IndexError as Error:
                logging.info('Não ha mais historico de dados a ser recolhido.')
                logging.info(Error)
                break

        return list_velas

def timestamp_converter(x): # Função para converter timestamp
    from datetime import datetime
    from dateutil import tz
    if isinstance(x, str):
        return x 
    hora = datetime.strptime(datetime.utcfromtimestamp(x).strftime('%Y-%m-%d %H:%M:%S'), '%Y-%m-%d %H:%M:%S')
    hora = hora.replace(tzinfo=tz.gettz('GMT'))
	
    return str(hora.astimezone(tz.gettz('America/Sao Paulo')))[:-6]

API = IqOption()
size = 60
goal= 'EURUSD'
API.API.start_candles_stream(goal, size, 1)
while True:
    candles = API.API.get_realtime_candles(goal, size)
    for c in candles:
        candle = candles[c]
        candle['from'] = timestamp_converter(candle['from'])
        candle['to'] = timestamp_converter(candle['to'])
        logging.info('candle\n %s', candle)
    time.sleep(5)