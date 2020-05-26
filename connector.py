import logging
import requests
import json  # https://www.json.org/json-en.html
import os
from schema import lines_directions, stops_ids
import datetime

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

client_id = os.environ['CLIENT_ID']
client_secret = os.environ['CLIENT_SECRET']
api_url_base = "https://apitransporte.buenosaires.gob.ar/"
api_url_subway = f"{api_url_base}subtes/"
api_url_subway_forecast = f"{api_url_subway}forecastGTFS?client_id={client_id}&client_secret={client_secret}"


def get_api_resp():
    res = requests.get(api_url_subway_forecast)
    if res.status_code == 200:  # Http status codes => https://developer.mozilla.org/es/docs/Web/HTTP/Status/200
        content = res.content
    else:
        return False
        # http://www.mocky.io/v2/5ecd56b43200004e002368dc => api response example
    return json.loads(content)


def get_forecast(data):
    try:
        resp = get_api_resp()
        if resp:  # https://www.freecodecamp.org/news/truthy-and-falsy-values-in-python/
            forecasts = next(filter(lambda x: filter_subway(x, data), resp['Entity']), None)['Linea']['Estaciones']
            user_station = next(filter(lambda x: x['stop_id'] == make_stop_id(data), forecasts), None)
            subway_arrival = user_station['arrival']['time']
            dt = (
                 datetime.datetime.fromtimestamp(subway_arrival) - datetime.datetime.now()
                 )
            if dt > datetime.timedelta(0):  # if negative, train is arriving
                user_forecast = f"El subte va a llegar en " \
                                f"{int(dt.total_seconds()//61)}:{str(int(dt.total_seconds()%61)).zfill(2)}" \
                                f" minutos!"
            else:
                user_forecast = "El subte esta llegando!"
            return user_forecast
        else:
            return "No se a donde pretendes ir a estas horas... pero el subte esta cerrado!"
    except TypeError as e:
        logger.error(e)
        return "Ups! Algo fallo, intenta otra vez!"


def filter_subway(entity, data):
    directions_mapper = {'S': 0, 'N': 1}
    # find element in JSON that matches line AND direction
    return f"Linea{data['line']}" in entity['ID'] and \
           entity['Linea']['Direction_ID'] == directions_mapper[lines_directions[data['line']][data['direction']]]


def make_stop_id(trip_info):
    return f"{stops_ids[trip_info['line']][trip_info['station']]}" \
           f"{lines_directions[trip_info['line']][trip_info['direction']]}"
