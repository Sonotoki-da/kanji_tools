import json
import sqlite3
from glob import glob
from main import BASE_DIR

connection = sqlite3.connect(BASE_DIR + "/sqlite.db")
for json_file in glob("**/japanese_core_*.json", recursive=True):
    with open(json_file) as f:
        connection.execute("")
