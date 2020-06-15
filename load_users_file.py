import json
import os


def get_users_from_file(file_name="users.json"):
    if os.path.exists(file_name):
        fp = open(file_name, "r")
        content = fp.read()
        fp.close()
        return json.loads(content)
