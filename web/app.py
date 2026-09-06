import os

from flask import Flask, request, render_template, redirect
from pymongo import MongoClient
from bson.objectid import ObjectId

app = Flask(__name__)

mongo_uri  = os.environ.get("MONGO_URI")
db_name    = os.environ.get("DB_NAME")

client = MongoClient(mongo_uri)
db = client[db_name]
routers = db['routers']

@app.route("/", methods=["GET"])
def main():
    return render_template("index.html", routers=list(routers.find()))

@app.route("/add", methods=["POST"])
def add_router():
    ip_address = request.form.get("ip_address")
    username = request.form.get("username")
    password = request.form.get("password")

    if ip_address and username and password:
        routers.insert_one({
            "ip_address": ip_address,
            "username": username,
            "password": password
        })
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete_router():
    router_id = request.form.get("router_id")
    routers.delete_one({"_id": ObjectId(router_id)})
    return redirect("/")

@app.route("/router/<ip_address>")
def router_detail(ip_address):
    interface_status = db['interface_status']
    status_history = list(interface_status.find({"router_ip": ip_address})
                          .sort("timestamp", -1)
                          .limit(3))
    return render_template("router_detail.html", ip_address=ip_address, status_history=status_history)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
