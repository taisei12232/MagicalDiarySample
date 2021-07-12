from azure.cosmos import exceptions, CosmosClient, PartitionKey
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
import json
from . import app

CORS(app)
# Initialize the Cosmos client
json_key = open('key.json', 'r')
endpoint = json.load(json_key)['endpoint']
key = json.load(json_key)['key']

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

# Create a database
# <create_database_if_not_exists>
database = client.get_database_client('MagicalDiary')
# </create_database_if_not_exists>

# Create a container
# Using a good partition key improves the performance of database operations.
# <create_container_if_not_exists>
container = database.get_container_client('User')
# </create_container_if_not_exists>

@app.route('/')
def home():
    return 'welcome!',200

@app.route('/read/<user_id>', methods=['GET'])
def read_user(user_id):
    try:
        item = container.read_item(user_id,user_id)
    except Exception:
        return '',404
    return item

@app.route('/rank', methods=['GET'])
def ranking():
    query = "SELECT i.id,i.name,i.count FROM items i ORDER BY i.count DESC"
    items = container.query_items(query, enable_cross_partition_query=True)
    return jsonify(list(items)),200

@app.route("/mypage/<user_id>", methods=['GET'])
def userPage(user_id):
    try:
        item = container.read_item(user_id,user_id)
    except Exception:
        return 'NotFound',404
    pages = {
        "name":item['name'],
        "begin":item['begin'],
        "count":item['count'],
        "energyDrinks":item['energyDrinks']
        }
    return jsonify(pages)

@app.route("/imagepost", methods=["POST"])
def result():
    user_id = request.form["user_id"]
    energyDrink = request.form["energyDrink"]
    try:
        read_item = container.read_item(user_id,user_id)
    except Exception:
        return '',404
    read_item['count'] += 1
    read_item['energyDrinks'] += [energyDrink]
    container.replace_item(item=read_item,body=read_item)
    return '',200

@app.route("/login",methods=["POST"])
def logIn():
    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    today = datetime.date.today()
    formatedToday = today.strftime('%Y/%m/%d')
    try:
        container.read_item(user_id,user_id)
    except Exception:
        user = {
            'id':user_id,
            'name':user_name,
            'begin':formatedToday,
            'count':0,
            'enargyDrinks':[]
        }
        container.create_item(body=user)
        return '',201
    return '',200
