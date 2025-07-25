ActivityStats
ActivityStats — это приложение для анализа и визуализации статистики игрового времени, собранной через стороннее приложение ActivityMonitor. Оно предоставляет пользователю удобный интерфейс для просмотра статистики, управления библиотекой игр и редактирования метаданных.
Описание
ActivityStats позволяет пользователям отслеживать и анализировать время, проведенное в играх, с помощью интерактивного интерфейса. 

Основной функционал:
1)	Отображение статистики игрового времени, включая общее время, среднюю продолжительность сессий, рекорды и визуализации в виде гистограмм и круговых диаграмм.
2)	Отображение итоговой статистики за выбранный год, включая метрики по игровому времени, жанрам, платформам и другим параметрам.
3)	Просмотр библиотеки игр, редактирование метаданные (жанр, год выпуска, рейтинг) и экспорт данных в PDF.

Функционал

Статистика игрового времени:

Отображение общего времени игры, средней продолжительности сессий и числа сессий.
Фильтрация данных по временному диапазону с помощью слайдера.
Визуализация статистики через круговые диаграммы и гистограммы (по дням недели и времени суток).
Отображение рекордов, таких как максимальная продолжительность сессии, самый активный день и серия игровых дней.

Итоги года:

Выбор года через выпадающее меню.
Подробная статистика за год, включая процент игрового времени, распределение по жанрам, платформам и другим метрикам.
Отображение "Игры года", процента времени в новинках и других интересных фактов.

Библиотека игр:

Просмотр списка игр в виде карточек с информацией о времени игры, жанре, годе выпуска и рейтинге.
Возможность редактирования метаданных (жанр, год, рейтинг, иконка) вручную или через автоматический парсинг (RAWG API).
Экспорт библиотеки в PDF.

Технологии

Язык программирования: Python 3.8+
Фреймворк: PySide6
Интерфейс: QML (Qt Quick 2.15, Qt Charts 2.15, Qt Quick Controls 2.15)
Сборка: PyInstaller 
База данных: PostgreSQL (для хранения данных об играх и статистике)
API: Интеграция с RAWG API для получения метаданных об играх (иконки, жанры, год выпуска)

Требования

Python 3.8 или выше
PySide6
PostgreSQL 13 или выше
PyInstaller (для сборки исполняемого файла)
Доступ к интернету для загрузки метаданных через RAWG API

Установка

Клонируйте репозиторий:
https://github.com/withoutfname/activitystat.git
cd activitystats


Установите зависимости:Создайте виртуальное окружение и установите необходимые пакеты:
python -m venv venv
На Windows: venv\Scripts\activate
pip install -r requirements.txt

Настройте базу данных PostgreSQL:

Установите PostgreSQL, если он еще не установлен.
Создайте базу данных:CREATE DATABASE activitydb;

Настройте конфигурацию:
cp config.example.json config.json

Откройте config.json и добавьте ваш API ключ для RAWG API и параметры базы данных. Пример структуры:
{
    "api_key": "YOUR_RAWG_API_KEY",
    "database": {
        "host": "YOUR_DB_HOST",
        "port": 5432,
        "database": "YOUR_DB_NAME",
        "user": "YOUR_DB_USER",
        "password": "YOUR_DB_PASSWORD"
    }
}

Запустите приложение:
python main.py

(Опционально) Сборка исполняемого файла:Для создания автономного исполняемого файла используйте PyInstaller:
pyinstaller.exe --name ActivityStats --onefile --noconsole --add-data "ui;ui" --add-data "src/backend;src/backend" --add-data "src/controllers;src/controllers" --add-data "resources;resources" --icon "resources/images/app_icon.ico" main.py

Использование

Запуск приложения:

Запустите main.py или собранный исполняемый файл.
Приложение автоматически подключится к базе данных и загрузит данные из ActivityMonitor.

Навигация:

Time: Используйте слайдер для выбора временного диапазона и просмотра статистики. Гистограммы и диаграммы обновляются автоматически.
Dashboard: Выберите год в выпадающем меню, чтобы увидеть итоговую статистику.
Library: Просматривайте игры, редактируйте метаданные через кнопки "Auto" (автоматический парсинг) или "Manual" (ручное редактирование). Экспортируйте библиотеку в PDF с помощью соответствующей кнопки.


Редактирование метаданных:

В разделе Library наведите курсор на карточку игры, чтобы открыть дополнительные данные.
Нажмите на кнопку "Manual" для ручного редактирования жанра, года, рейтинга или иконки.
Используйте кнопку "Auto" для автоматической загрузки метаданных через RAWG API.

Нажмите кнопку "Export to PDF" в разделе Library для создания PDF-отчета.
