import psycopg2
from psycopg2 import Error
import json
import os

# src/backend/database/database.py
class Database:
    def __init__(self):
        self.connection = None
        self.cursor = None
        self._base_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../.."))
        self.db_params = self._load_config()
        self.connect()
        self._create_tables_if_not_exist()


    def _load_config(self):
        """Загружает конфигурацию из config.json в корне проекта."""
        config_path = os.path.join(self._base_path, "config.json")
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                db_config = config.get("database", {})
                return {
                    'dbname': db_config.get("database"),
                    'user': db_config.get("user"),
                    'password': db_config.get("password"),
                    'host': db_config.get("host"),
                    'port': str(db_config.get("port"))
                }
        except FileNotFoundError:
            print(f"Ошибка: Файл конфигурации {config_path} не найден")


    def connect(self):
        try:
            if self.connection is not None and not self.connection.closed:
                self.close()

            self.connection = psycopg2.connect(**self.db_params)
            self.connection.autocommit = True
            self.cursor = self.connection.cursor()
            self._create_tables_if_not_exist()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection and not self.connection.closed:
            self.connection.close()
        print("Database connection closed")

    def _create_tables_if_not_exist(self):
        """Создает таблицы, если они не существуют"""
        try:
            # Создание таблицы apps
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.apps (
                    id integer NOT NULL,
                    name character varying(255) NOT NULL,
                    exe_path character varying(255),
                    process_name character varying(255),
                    alias character varying(255) NOT NULL,
                    CONSTRAINT apps_pkey PRIMARY KEY (id)
                )
            """)

            # Создание последовательности для apps_id_seq
            self.cursor.execute("""
                CREATE SEQUENCE IF NOT EXISTS public.apps_id_seq
                    AS integer
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1
            """)

            # Создание таблицы activity_sessions
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.activity_sessions (
                    id integer NOT NULL,
                    app_id integer NOT NULL,
                    start_time timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
                    end_time timestamp without time zone,
                    is_tracking boolean DEFAULT true,
                    CONSTRAINT activity_sessions_pkey PRIMARY KEY (id),
                    CONSTRAINT activity_sessions_app_id_fkey FOREIGN KEY (app_id)
                        REFERENCES public.apps(id)
                )
            """)

            # Создание последовательности для activity_sessions_id_seq
            self.cursor.execute("""
                CREATE SEQUENCE IF NOT EXISTS public.activity_sessions_id_seq
                    AS integer
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1
            """)

            # Создание таблицы game_metadata
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.game_metadata (
                    app_id integer NOT NULL,
                    icon_path text,
                    genre text,
                    year integer,
                    rating text,
                    CONSTRAINT game_metadata_pkey PRIMARY KEY (app_id),
                    CONSTRAINT game_metadata_app_id_fkey FOREIGN KEY (app_id)
                        REFERENCES public.apps(id) ON DELETE CASCADE
                )
            """)

            # Создание таблицы tracked_apps
            self.cursor.execute("""
                CREATE TABLE IF NOT EXISTS public.tracked_apps (
                    id integer NOT NULL,
                    app_id integer NOT NULL,
                    CONSTRAINT tracked_apps_pkey PRIMARY KEY (id),
                    CONSTRAINT tracked_apps_app_id_fkey FOREIGN KEY (app_id)
                        REFERENCES public.apps(id)
                )
            """)

            # Создание последовательности для tracked_apps_id_seq
            self.cursor.execute("""
                CREATE SEQUENCE IF NOT EXISTS public.tracked_apps_id_seq
                    AS integer
                    START WITH 1
                    INCREMENT BY 1
                    NO MINVALUE
                    NO MAXVALUE
                    CACHE 1
            """)

            # Установка значений по умолчанию для id в таблицах
            self.cursor.execute("""
                ALTER TABLE ONLY public.activity_sessions
                ALTER COLUMN id SET DEFAULT nextval('public.activity_sessions_id_seq'::regclass)
            """)

            self.cursor.execute("""
                ALTER TABLE ONLY public.apps
                ALTER COLUMN id SET DEFAULT nextval('public.apps_id_seq'::regclass)
            """)

            self.cursor.execute("""
                ALTER TABLE ONLY public.tracked_apps
                ALTER COLUMN id SET DEFAULT nextval('public.tracked_apps_id_seq'::regclass)
            """)

            print("Tables created successfully or already exist")

        except Error as e:
            print(f"Error creating tables: {e}")
            raise

