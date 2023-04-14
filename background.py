import sys
from pithy3 import *
from glob import glob
import xmltodict as xd
from exif import Image
import json
import sqlite3
from sqlite_utils import Database
from subprocess import getoutput as go

settings = json.load(open("settings.json"))
base_dir = settings['directory_base']

def clear_jpgs():
    g2 = glob(f"{base_dir}/sem/**/*.jpg")
    for g in g2: print(go(f"rm '{g}'"))

def scanner():
    g1 = glob(f"{base_dir}/sem/**/*.tiff")
    g2 = glob(f"{base_dir}/sem/**/*.jpg")
    g1p = [g.replace(".tiff","") for g in g1 ]
    g2p = [g.replace(".jpg","") for g in g2  ]
    gtc = set(g1p)-set(g2p)
    gtc = [g+".tiff" for g in list(gtc)]
    return gtc

def get_meta(fn):
    with tifffile.TiffFile(fn) as tif:
        tif_tags = {}
        for tag in tif.pages[0].tags.values():
            name, value = tag.name, tag.value
            tif_tags[name] = value
    meta = xd.parse(tif_tags['FEI_TITAN'])
    return json.dumps(meta)


def build_database():
    fndb = f"{base_dir}/db.sqlite3"
    db = Database(fndb)
    jsons = glob(f"{base_dir}/sem/**/*.json")
    out = []
    for j in jsons: 
        o = json.loads(open(j).read())['FeiImage']
        out.append({'time':o['time'],
                    'img':j.replace(".json",".jpg"),
                    'user':j.split("/")[5],
                    'label':str(j.split("/")[6:]).replace(".json",""),
                    'json':o})
    db['table'].insert_all(out,pk="time",alter=True,upsert=True)


def convert_tiffs():
    count = 0
    ttc = scanner()
    for t in ttc:
        try:
            count +=1
            meta = get_meta(t)
            fnjson = t.replace(".tiff",".json")
            fnjpg = t.replace(".tiff",".jpg")
            open(fnjson,'w').write(meta)
            print(go(f"convert '{t}' -quality 80 '{fnjpg}'"))
        except:
            print(t)


if __name__ == "__main__":

    if len(sys.argv) == 1:
        print("we'll do stuff when you tell us to")
        exit()

    if "convert_tiffs" in sys.argv: 
        print("converting tiffs....",end="") 
        convert_tiffs()
        print("done")

    if "clear_jpgs" in sys.argv: 
        print("clearing jpgs....",end="") 
        clear_jpgs()
        print("done") 

    if "build_database" in sys.argv:
        print("building database....",end="") 
        build_database()
        print("done") 
        
