from flask import Flask,send_from_directory
import os
from PIL import Image
import pandas as pd
import sqlite3 as sql
import time, threading
from glob import glob
import json

StartTime=time.time()

settings = json.load(open("settings.json"))
base_dir = settings['directory_base']
http_port = settings['http_port']
app = Flask(__name__)
fndb = f"{base_dir}/db.sqlite3"


@app.route("/")
def home():  return open("index.html").read()

@app.route("/measure/<path:path>")
def measure(path):  return open("measure.html").read()


@app.route("/dird")
def dird():  return json.dumps(glob(f"{base_dir}/sem/**/*.json"))


@app.route("/sems")
def sems():  
    q = "SELECT * from `table`"
    df = pd.read_sql(q,con=sql.connect(fndb))
    df['img'] = df['img'].apply(lambda x: x)
    return df[['time','user','label','img']].to_html(table_id='data',index=None)



@app.route('/drops/<path:path>')
def send_file(path):
    return send_from_directory('/drops', path)


app.run(host="0.0.0.0",port=http_port,debug=True)