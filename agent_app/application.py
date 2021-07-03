from azure.cosmos import exceptions, CosmosClient, PartitionKey
from flask import Flask, jsonify, request
from flask_cors import CORS
import datetime
from . import app

CORS(app)
# Initialize the Cosmos client
endpoint = "https://agentserver.documents.azure.com:443/"
key = 'xRyACyJ8SEBhfGm7ZdcPThYvpkyPFcMmD8o8iKTDhI8HJUKfByFr0hvoactFQF7bb0Nq1TF12dzxqfWmCjeDBA=='

# <create_cosmos_client>
client = CosmosClient(endpoint, key)
# </create_cosmos_client>

# Create a database
# <create_database_if_not_exists>
database = client.get_database_client('MagicalDiary')
# </create_database_if_not_exists>
database
# Create a container
# Using a good partition key improves the performance of database operations.
# <create_container_if_not_exists>
container_name = 'User'
container = database.get_container_client(container_name)
container

# </create_container_if_not_exists>
@app.route('/')
def home():
    return 'welcome!',200
@app.route('/read/<user_id>', methods=['GET'])
def read_user(user_id):
    try:
        item = container.read_item(user_id,user_id)
    except:
        return 'てやんでい！そんなユーザーは存在しねぇぜ！一昨日きやがれ！',404
    return item
@app.route('/rank')
def ranking():
    query = "SELECT i.id,i.name,i.count FROM items i ORDER BY i.count DESC"
    items = container.query_items(query, enable_cross_partition_query=True)
    return jsonify(list(items))
@app.route("/mypage/<user_id>")
def yourPage(user_id):
    try:
        item = container.read_item(user_id,user_id)
    except:
        return '', 404
    pages = {"name":item['name'],"start":item['start'],"count":item['count'],"monster":item['monster']}
    return jsonify(pages)
@app.route("/imagepost", methods=["POST"])
def result():
    user_id = request.form["user_id"]
    agent = request.form["agent"]
    try:
        read_item = container.read_item(user_id,user_id)
    except:
        return '', 404
    read_item['count'] += 1
    read_item['monster'] += [agent]
    response = container.replace_item(item=read_item, body=read_item)
    return '', 204
@app.route("/login",methods=["POST"])
def logIn():
    user_id = request.form["user_id"]
    user_name = request.form["user_name"]
    today =  datetime.date.today()
    today = today.strftime('%Y/%m/%d')
    try:
        container.read_item(user_id,user_id)
    except:
        user = {
            'id':user_id,
            'name':user_name,
            'start':today,
            'count':0,
            'monster':[]
        }
        container.create_item(body=user)
    return '', 204
