# src/backend/services/backup_service.py
import os
import subprocess
import time
from PySide6.QtCore import QObject, Signal

class BackupService(QObject):
    backupCompleted = Signal(bool, str)  # success, message
    restoreCompleted = Signal(bool, str)  # success, message

    def __init__(self, db_config, database):
        super().__init__()
        self.db_config = db_config
        self.database = database  # Добавляем ссылку на Database

    def backup_database(self, file_path):
        try:
            os.makedirs(os.path.dirname(file_path), exist_ok=True)
            command = [
                'pg_dump',
                '-U', self.db_config['user'],
                '-d', self.db_config['dbname'],
                '-f', file_path,
                '-h', self.db_config['host'],
                '-p', self.db_config['port']
            ]
            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']

            result = subprocess.run(command, env=env, capture_output=True, text=True)

            if result.returncode == 0:
                self.backupCompleted.emit(True, f"Backup saved to {file_path}")
            else:
                self.backupCompleted.emit(False, f"Backup failed: {result.stderr}")

        except Exception as e:
            self.backupCompleted.emit(False, f"Backup error: {str(e)}")

    def restore_database(self, file_path):
        try:
            # Закрываем все соединения с БД
            self.database.close()

            # Даем время на закрытие соединений
            time.sleep(1)

            # Терминация всех активных подключений
            terminate_cmd = [
                'psql',
                '-U', self.db_config['user'],
                '-h', self.db_config['host'],
                '-p', self.db_config['port'],
                '-d', 'postgres',  # Подключаемся к системной БД
                '-c', f"SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity WHERE pg_stat_activity.datname = '{self.db_config['dbname']}' AND pid <> pg_backend_pid();"
            ]

            env = os.environ.copy()
            env['PGPASSWORD'] = self.db_config['password']

            subprocess.run(terminate_cmd, env=env, capture_output=True, text=True)

            # Восстановление БД
            commands = [
                [
                    'psql',
                    '-U', self.db_config['user'],
                    '-h', self.db_config['host'],
                    '-p', self.db_config['port'],
                    '-d', 'postgres',
                    '-c', f"DROP DATABASE IF EXISTS {self.db_config['dbname']};"
                ],
                [
                    'psql',
                    '-U', self.db_config['user'],
                    '-h', self.db_config['host'],
                    '-p', self.db_config['port'],
                    '-d', 'postgres',
                    '-c', f"CREATE DATABASE {self.db_config['dbname']};"
                ],
                [
                    'psql',
                    '-U', self.db_config['user'],
                    '-d', self.db_config['dbname'],
                    '-h', self.db_config['host'],
                    '-p', self.db_config['port'],
                    '-f', file_path
                ]
            ]

            for cmd in commands:
                result = subprocess.run(cmd, env=env, capture_output=True, text=True)
                if result.returncode != 0:
                    raise Exception(result.stderr)

            # Переподключаемся к восстановленной БД
            self.database.connect()

            self.restoreCompleted.emit(True, "Database restored successfully")

        except Exception as e:
            self.restoreCompleted.emit(False, f"Restore error: {str(e)}")
            # Пытаемся переподключиться даже после ошибки
            try:
                self.database.connect()
            except:
                pass
