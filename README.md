## Telegram-bot для Yandex.Praktikum.Home

### Описание проекта
  - Обращается к API сервиса Yandex.Praktikum.Home и каждые 10 минут проверяет
статус проекта (присылает уведомление при изменении статуса).
  - Логирует свою работу и присылает уведомление в случае ошибки.

### Основные технологии:
* Python
* Python-telegram-bot

### Перед запуском проекта необходимо наличие двух токенов и id вашего аккаунта в Telegram:
 - Токен API Yandex.Praktikum - получить токен можно по этой [ссылке](https://oauth.yandex.ru/authorize?response_type=token&client_id=1d0b9dd4d652455a9eb710d450ff456a),
если вы являетесь студентом одного из курсов в Yandex.Praktikum.
 - Токен вашего Telegram-бота.
    Как создать и получить токен можно посмотреть [здесь](https://core.telegram.org/bots).
 - ID вашего аккаунта Telegram (для его получения можно воспользоваться одним
из этих ботов: [@getmyid_bot](https://t.me/getmyid_bot) 
или [@userinfobot](https://telegram.me/userinfobot))

### Как запустить проект:
 -  Клонировать репозиторий:

```
git clone 'ссылка на репозиторий'
```

 -  Cоздать и активировать виртуальное окружение:

```
python -m venv env
```
```
source env/bin/activate
```
```
python -m pip install --upgrade pip
```

 -  Установить зависимости из файла requirements.txt:

```
pip install -r requirements.txt
```

 -  Создать файл .env в основной папке со следующим содержанием:

```
PRACTICUM_TOKEN=your_practicum_homework_token
TELEGRAM_TOKEN=your_telegram_bot_token
TELEGRAM_CHAT_ID=your_telegram_chat_id
```

 -  Запустить проект:

```
python homework.py
```

После запуска проекта написать своему боту для старта отслеживания статуса ваших домашних работ. 

**Автор**  
Стацюк В.Н.
