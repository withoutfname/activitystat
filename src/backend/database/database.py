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
            self._create_tables_if_not_exist()
            print("Database connection successful")
        except Error as e:
            print(f"Error connecting to database: {e}")
            raise

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

    def close(self):
        if self.cursor:
            self.cursor.close()
        if self.connection:
            self.connection.close()
            print("Database connection closed")
