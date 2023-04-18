import mysql.connector
from utils.cache import get_conf

config = {
  'user': get_conf("mysql_user"),
  'password': get_conf("mysql_pwd"),
  'host': get_conf("mysql_url"),
  'database': 'wx',
  'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)

