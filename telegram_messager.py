"""
A daily telegram messager bot that sends the weather information every morning.

Units are turned to Celcius. 
Created a Turkish dict to be added in the message for some specific weather conditions.

Requires a telegram bot created by using telegram's 'BotFather'
"""

import telegram_send as ts
import requests, json, random

#Get weather info
def get_weather():
        open_weather_api = '' #--------------------------------------------------------------------> your api here

        base_url = "http://api.openweathermap.org/data/2.5/weather?"
        city_name = '' #--------------------------------------------------------------------> your city here
        complete_url = base_url + "appid=" + open_weather_api + "&q=" + city_name
        response = requests.get(complete_url)
        response = response.json()
        if response['cod'] != '404':
                curr_temp = int(float(response['main']['temp']) - 273.15)
                curr_humi = response['main']['humidity']
                feel_temp = int(float(response['main']['feels_like']) - 273.15)
                desc = response['weather'][0]['description']

                return curr_temp, curr_humi, feel_temp, desc

#en-tr dictionary
weather_dict = { 'few clouds':'az bulutlu', 'scattered clouds':'parçalı bulutlu',
                'broken clouds':'bulutlu', 'shower rain':'sağanak yağışlı', 'clear sky':'açık',
                'rain':'yağmurlu', 'thunderstorm':'fırtınalı', 'snow':'karlı', 'mist':'sisli',
                'light rain':'hafif yağmurlu' }

curr_temp, curr_humi, feel_like, desc = get_weather()
try: desc = weather_dict[desc]
except: pass

#Words to randomly choose from
greetings = ['Morning', 'Günaydın', 'Gün başladı', 'Yeni bir güne merhaba']

#Preparing message
message = """
{}

Hava durumu: {}
Şuan ki hava sıcaklığı {} derece civarında.
Havanın nem oranı ise yüzde {}.
Hissedilen sıcaklık {} derece deniyor.

""" #--------------------------------------------------------------------> your message here
message = message.format(\
                random.choice(greetings),
                desc, curr_temp, curr_humi, feel_like,
)
#Add some precautions incase of rain or snow
if 'yağmurlu' in desc: message = message + " Bir şemsiye almak ve bot giymek de iyi olabilir. "
elif 'karlı' in desc: message = message + " Eldiven ve atkıları da kuşan istersen. "

#Send message
ts.send(messages = [message])