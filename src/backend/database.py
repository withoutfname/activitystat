import psycopg2
from psycopg2 import Error

class Database:
    def __init__(self, dbname="activitydb", user="postgres", password="pass", host="localhost", port="5432"):
        self.connection = None
        self.cursor = None
        try:
            self.connection = psycopg2.connect(
                dbname=dbname,
                user=user,
                password=password,
                host=host,
                port=port
            )
            self.connection.autocommit = True  # Включаем автокоммит
            self.cursor = self.connection.cursor()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed")