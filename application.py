from flask import Flask, render_template, request
import requests
from zeep import Client
import json
import random
import xml.etree.ElementTree as et
from datetime import datetime

app = Flask(__name__)


def weather(zipcode):
    # this the soap client that uses the wsdl document
    client = Client(wsdl='https://graphical.weather.gov/xml/DWMLgen/wsdl/ndfdXML.wsdl')
    # client is used to contact soap server, it calls on the service LatLonListZipCode
    # this service takes in a zipcode and provides the latitude and longitude of the zipcode
    xml = client.service.LatLonListZipCode(zipcode)
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


def ingredients(weather):
    # apiKey = "b416b50949e34e9cb96c59491176eda6"
    apiKey = "dd7f4afe91d94e0a8513f59020b309c9"
    foods = []
    recipes = []
    if weather == "cold":
        foods = ["oatmeal", "black bean", "brussels sprouts", "pumpkin", "chili", "avocado", "walnuts",
                 "apples", "sweet potatoes", "squash", "radish", "turnip", "eggs", "cabbage", "carrots", "chicken",
                 "beef", "pork", "turkey"]
    elif weather == "rain":
        foods = ["pointed gourd", "macaroni", "butternut squash",
                 "chicken", "potatoes", "Mushroom", "beans", "ham",
                 "tomato", "chili", "spinach", "turkey", "peas",
                 "broccoli", "cabbage", "celery", "split pea", "eggs",
                 "corn", "salmon", "broccoli", "tofu",
                 "bell pepper", "noodles", "mushroom"]
    elif weather == "hot":
        foods = ["mozzarella", "spinach", "Cucumbers", "radishes",
                 "celery", "zucchini", "Watermelon", "honeydew",
                 "cantaloupe", "pears", "apples", "bananas", "squash",
                 "broccoli", "asparagus", "swiss chard", "turnips", "watercress",
                 "cucumbers", "radishes", "alfalfa", "soybean", "sprouts", "avocado"]
    random.shuffle(foods)
    food_list = foods[:3]
    # print(food_list)
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
            temp.append((i['title'], i['image']))
            for j in i['missedIngredients']:
                temp.append((j["name"], j['image']))
                # print(j["name"], j['image'])
            for j in i['usedIngredients']:
                temp.append((j["name"], j['image']))
                # print(j["name"], j['image'])
            # random.shuffle(temp)
            recipes.append(temp)
            # print("*" * 40)
    # print(recipes)
    return recipes


def walmart(ingredient):
    url = ""
    cost = 0
    cost_list = []
    for i in ingredient:
        base_url = "https://grocery.walmart.com/v4/api/"
        headers = {
            "path": "products/search"
        }
        qstring = {
            'storeId': '1619',
            'count': '1',
            'page': '1',
            'offset': '0',
            'query': i

        }

        data = requests.get(base_url + 'products/search', headers=headers, params=qstring).text
        aDict = json.loads(data)
        for key, value in aDict.items():
            if (key == "products"):
                for element in value:
                    url = element['basic']['image']['thumbnail']
                    cost = element['store']['price']['list']
                    # print(element['basic']['image']['thumbnail'])
                    # print(element['store']['price']['list'])
                    cost_list.append([cost, url])
    return cost_list


def recipe(weather_data):
    # print(weather_data)
    weather = ""
    if ("Freez" in weather_data[2] or "Snow" in weather_data[2]
            or "Ice" in weather_data[2] or "Flurr" in weather_data[2]
            or "Wint" in weather_data[2] or int(weather_data[1]) < 37):
        weather = "cold"
    elif ("Rain" in weather_data[2] or "Sleet" in weather_data[2] or "Drizzle" in weather_data[2]
          or "Shower" in weather_data[2]):
        weather = "rain"
    else:
        weather = "hot"

    food = ingredients(weather)
    random.shuffle(food)

    return food[:3]


# @app.route('/temperature', methods=['POST'])
def temperature():
    zipcode = request.form['zip']
    temp_data = weather(zipcode)
    list_recipes = []
    for i in temp_data:
        for j in recipe(i):
            list_recipes.append(j)

    list_ingredients = []

    for i in list_recipes:
        temp_ing = []
        temp_url = []
        for j in i[1:len(i)]:
            temp_ing.append(j[0])
            temp_url.append(j[1])
        list_ingredients.append((temp_ing, temp_url))

    wal_cost_list = []
    wal_url_list = []
    for i in list_ingredients:
        temp_list = walmart(i[0])
        temp_url = []
        temp_cost = []
        for j in temp_list:
            temp_cost.append(j[0])
            temp_url.append(j[1])
        wal_cost_list.append(temp_cost)
        wal_url_list.append(temp_url)

    return render_template('temperature.html',
                           date1=temp_data[0][0], temp1=temp_data[0][1], cond1=temp_data[0][2], url1=temp_data[0][3],
                           rcp1=list_recipes[0][0][0], len1=len(list_ingredients[0][0]), ing1=list_ingredients[0][0],
                           ing_url1=list_ingredients[0][1],
                           rcp_url1=list_recipes[0][0][1],
                           wal_cost1=wal_cost_list[0], wal_url1=wal_url_list[0],
                           date2=temp_data[1][0], temp2=temp_data[1][1], cond2=temp_data[1][2], url2=temp_data[1][3],
                           rcp2=list_recipes[1][0][0],
                           rcp_url2=list_recipes[1][0][1],
                           len2=len(list_ingredients[1][0]), ing2=list_ingredients[1][0],
                           ing_url2=list_ingredients[1][1],
                           wal_cost2=wal_cost_list[1], wal_url2=wal_url_list[1],
                           date3=temp_data[2][0], temp3=temp_data[2][1], cond3=temp_data[2][2], url3=temp_data[2][3],
                           rcp3=list_recipes[2][0][0],
                           rcp_url3=list_recipes[2][0][1],
                           len3=len(list_ingredients[2][0]), ing3=list_ingredients[2][0],
                           ing_url3=list_ingredients[2][1],
                           wal_cost3=wal_cost_list[2], wal_url3=wal_url_list[2],
                           date4=temp_data[3][0], temp4=temp_data[3][1], cond4=temp_data[3][2], url4=temp_data[3][3],
                           rcp4=list_recipes[3][0][0],
                           rcp_url4=list_recipes[3][0][1],
                           len4=len(list_ingredients[3][0]), ing4=list_ingredients[3][0],
                           ing_url4=list_ingredients[3][1],
                           wal_cost4=wal_cost_list[3], wal_url4=wal_url_list[3],
                           date5=temp_data[4][0], temp5=temp_data[4][1], cond5=temp_data[4][2], url5=temp_data[4][3],
                           rcp5=list_recipes[4][0][0],
                           rcp_url5=list_recipes[4][0][1],
                           len5=len(list_ingredients[4][0]), ing5=list_ingredients[4][0],
                           ing_url5=list_ingredients[4][1],
                           wal_cost5=wal_cost_list[4], wal_url5=wal_url_list[4],
                           date6=temp_data[5][0], temp6=temp_data[5][1], cond6=temp_data[5][2], url6=temp_data[5][3],
                           rcp6=list_recipes[5][0][0],
                           rcp_url6=list_recipes[5][0][1],
                           len6=len(list_ingredients[5][0]), ing6=list_ingredients[5][0],
                           ing_url6=list_ingredients[5][1],
                           wal_cost6=wal_cost_list[5], wal_url6=wal_url_list[5],
                           date7=temp_data[6][0], temp7=temp_data[6][1], cond7=temp_data[6][2], url7=temp_data[6][3],
                           rcp7=list_recipes[6][0][0], rcp_url7=list_recipes[6][0][1], len7=len(list_ingredients[6][0]),
                           ing7=list_ingredients[6][0],
                           ing_url7=list_ingredients[6][1],
                           wal_cost7=wal_cost_list[6], wal_url7=wal_url_list[6],
                           )


# @app.route('/')
def index():
    return render_template('index.html')


if __name__ == '__main__':
    app.jinja_env.cache = {}
    app.run(debug=True)
