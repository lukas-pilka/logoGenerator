import os
import pymysql

# Loads cloudSQL access data for connection from localhost
db_user = os.environ.get('CLOUD_SQL_USERNAME')
db_password = os.environ.get('CLOUD_SQL_PASSWORD')
db_name = os.environ.get('CLOUD_SQL_DATABASE_NAME')
db_connection_name = os.environ.get('CLOUD_SQL_CONNECTION_NAME')

def cloudSqlCnx():
    # When deployed to App Engine, the `GAE_ENV` environment variable will be set to `standard`
    if os.environ.get('GAE_ENV') == 'standard':
        # If deployed, use the local socket interface for accessing Cloud SQL
        unix_socket = '/cloudsql/{}'.format(db_connection_name)
        cnx = pymysql.connect(user=db_user, password=db_password, unix_socket=unix_socket, db=db_name)
        return cnx
    else:
        # If running locally, use the TCP connections
        host = '34.107.110.174'
        cnx = pymysql.connect(user=db_user, password=db_password, host=host, db=db_name)
        return cnx
