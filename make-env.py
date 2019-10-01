#!/usr/bin/python3
import os

with open("db.env", "w") as f:
    f.write("FLASK_APP=main\n")
    f.write("POSTGRES_HOST=postgres\n")
    f.write("POSTGRES_DB=zonemonitor\n")
    f.write("POSTGRES_USER=postgres\n")
    f.write("POSTGRES_PASSWORD={}\n".format(os.urandom(16).hex()))

