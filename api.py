"""
Please note this is a test page where all the methods were tested.
The main pages of the application are application.py and weather_api.py

"""
from flask import Flask, render_template, request
import requests
import zeep
from zeep import Client
import bs4
from bs4 import BeautifulSoup as bs
import re
import json
import random
import xml.etree.ElementTree as et
from datetime import datetime
from random import choices

app = Flask(__name__)


@app.route('/temperature', methods=['POST'])
def temperature():
    zipcode = request.form['zip']
    req = requests.get(
        'http://api.openweathermap.org/data/2.5/weather?zip=' + zipcode + ',us&appid=9be50413613f7c1337bf95e54370c672')
    temp = float(req.json()['main']['temp'])
    # return str(temp)
    far = str(((temp - 273.15) * 9 / 5) + 32)

    return render_template('temperature.html', temp=far)


@app.route('/')
def index():
    return render_template('index.html')


def weather():
    # this the soap client that uses the wsdl document
    client = Client(wsdl='https://graphical.weather.gov/xml/DWMLgen/wsdl/ndfdXML.wsdl')
    # client is used to contact soap server, it calls on the service LatLonListZipCode
    # this service takes in a zipcode and provides the latitude and longitude of the zipcode
    xml = client.service.LatLonListZipCode(14623)
    # xml returned is a string and it is parsed
    data = et.fromstring(xml)
    latlong = data[0].text.split(",")
    # the latitude and longitude obtained from the previous step is used to call another service NDFDgenByDay
    # it takes in the lat and long and gives weather prediction for the next 7 days
    today = str("'") + datetime.today().strftime('%Y-%m-%d') + str("'")
    xml = client.service.NDFDgenByDay(latlong[0], latlong[1], today, 7, 'e', '24 hourly')
    data = et.fromstring(xml)
    # print(xml)
    # the xml is extracted from the string and using xpath we access the necessary information. In order to
    # find out more about the xml, comment out the print(xml) line.
    temp_data = []
    for i in range(0, 7):
        temp_data.append([])
    count = 0
    for i in data.findall("./data/time-layout[@summarization=\"24hourly\"]/start-valid-time"):
        if (count > 6):
            break
        date = i.text[:10]
        date_str = date[-5:-3] + str("-") + date[-2:] + str("-") + date[:4]
        temp_data[count].append(date_str)
        count += 1

    count = 0

    for i in data.findall("./data/parameters/temperature[@type=\"maximum\"]/value"):
        temp_data[count].append(i.text)
        count += 1
    count = 0
    for i in data.findall("./data/parameters/weather/weather-conditions"):
        temp_data[count].append(i.attrib["weather-summary"])
        count += 1
    count = 0
    for i in data.findall("./data/parameters/conditions-icon/icon-link"):
        temp_data[count].append(i.text)
        count += 1
    return temp_data


def amazon():
    url = "https://ultimate-amazon-data-scrapers.p.rapidapi.com/amz-bestsellers/"

    querystring = {"url": "https://www.amazon.com/Best-Sellers-Mens-Outerwear-Jackets-Coats/zgbs/fashion/1045830"}

    headers = {
        'x-rapidapi-host': "ultimate-amazon-data-scrapers.p.rapidapi.com",
        'x-rapidapi-key': "40edb6c566mshca3e2f4ba6965aep169a1cjsn996bb67e2ee5"
    }

    response = requests.request("GET", url, headers=headers, params=querystring)

    print(response.text)


def walmart(ingredient):
    base_url = "https://grocery.walmart.com/v4/api/"
    headers = {
        "path": "products/search"
    }
    qstring = {
        'storeId': '1619',
        'count': '10',
        'page': '1',
        'offset': '0',
        'query': ingredient

    }

    # headers_store={"path":"finder"}
    # q_store={"location":"55344","distance":"10"}
    data = requests.get(base_url + 'products/search', headers=headers, params=qstring).text
    aDict = json.loads(data)
    for key, value in aDict.items():
        if (key == "products"):
            for element in value:
                print(element['basic']['image']['thumbnail'])
                print(element['store']['price']['list'])
    # sample = requests.get("https://www.walmart.com/store", headers=headers_store, params=q_store).text

    # URL = 'https://www.walmart.com/store/finder?location=55344&distance=10'
    # page = requests.get(URL)
    # sample = bs(page.content,'html.parser')
    # print(sample.text)
    # pattern = re.compile(r"\"store\":")
    # data = pattern.search(sample.text)
    # print(data)
    # # print(soup.find("publishedDate"))

def ingredients(weather):
    # apiKey = "dd7f4afe91d94e0a8513f59020b309c9"
    apiKey = "b416b50949e34e9cb96c59491176eda6"
    foods = []
    recipes = []
    if weather == "cold":
        foods = ["oatmeal", "black bean", "brussels sprouts", "pumpkin", "chili", "avocado", "walnuts",
                 "apples", "sweet potatoes", "squash", "radish", "turnip", "eggs", "cabbage", "carrots", "chicken",
                 "beef", "pork", "turkey"]
    elif weather == "rain":
        foods=["pointed gourd", "macaroni", "butternut squash",
               "chicken", "potatoes", "Mushroom", "beans", "ham",
               "tomato", "chili", "spinach", "turkey", "peas",
               "broccoli", "cabbage", "celery", "split pea", "eggs",
               "corn", "salmon", "broccoli", "tofu",
               "bell pepper", "noodles", "mushroom"]
    elif weather == "hot":
        foods=["mozzarella", "spinach", "Cucumbers", "radishes",
               "celery", "zucchini", "Watermelon", "honeydew",
               "cantaloupe", "pears", "apples", "bananas", "squash",
               "broccoli", "asparagus", "swiss chard", "turnips", "watercress",
               "cucumbers", "radishes", "alfalfa", "soybean", "sprouts", "avocado"]
    random.shuffle(foods)
    food_list = foods[:3]
    print(food_list)
    for i in food_list:

        req = requests.get(
            'https://api.spoonacular.com/recipes/findByIngredients?ingredients='
            + i + '&number=5&apiKey=' + apiKey)
        # req=requests.get('https://api.spoonacular.com/food/products/search?query=yogurt&apiKey='+apiKey)
        aDict = json.loads(req.text)
        # print(aDict)
        for i in aDict:
            temp = []
            # print("Recipe = ",i['title'])
            # print(i["image"])
            temp.append((i['title'],i['image']))
            for j in i['missedIngredients']:
                temp.append((j["name"], j['image']))
                # print(j["name"], j['image'])
            for j in i['usedIngredients']:
                temp.append((j["name"], j['image']))
                # print(j["name"], j['image'])
        # random.shuffle(temp)
            recipes.append(temp)
            # print("*" * 40)
    return recipes


def recipe(weather_data):
    # print(weather_data)
    weather = ""
    food=[]
    for i in weather_data:
        print(i[2])
        if("Freez" in i[2] or "Snow" in i[2]
                or "Ice" in i[2] or "Flurr" in i[2]
            or "Wint" in i[2] or int(i[1])<37):
            weather = "cold"
        elif ("Rain" in i[2] or "Sleet" in i[2] or "Drizzle" in i[2]
                or "Shower" in i[2]):
            weather="rain"
        else:
            weather = "hot"

        food = ingredients(weather)


    return food


if __name__ == '__main__':
    # app.run(debug=True)
    # weather()
    # amazon()
    # walmart()
    recipes = recipe(weather())
    random.shuffle(recipes)
    for i in recipes[:3]:
        print(i)
