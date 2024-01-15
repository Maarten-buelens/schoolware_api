
# Schoolware-api
An api for schoolware written in python

## Capabilities
* get agenda points
* get scores
* get todo items
* send telegram message for new scores
* support for microsoft and schoolware login

## Config
| Key | Description |
| --- | --- |
| domain | domain name of schoolware
| user | school microsoft email
| password | school microsoft password
| schoolware_login | set true if using schoolware login
| telegram_enabled | required to enable telegram
| telegram_bot_token | telegram bot token to enable telegram bot
| telegram_chat_id | id to send messages to
| verbose | show a some more info, when what function is run
| debug | show a lot more info, all networking info

## Install
* `pip3 install schoolware_api --upgrade `
* `playwright install &&  playwright install-deps` only for microsoft login 

## optional
* `pip3 install python-telegram-bot` needed for telegram

## Simple example

```python
from schoolware_api import schoolware

config = {"domain":"", "user":"", "password":""} #example domain: kov.schoolware.be user: name.lastname@leerling.kov.be password: password 

Schoolware = schoolware(config)

print(Schoolware.todo())  # Returns all todo items
print(Schoolware.punten()) # Returns all scores this schoolyear
print(Schoolware.agenda()) # Returns agenda points today
print(Schoolware.agenda(datum="2023-03-06 00:00:00")) # Returns agenda points for 2023-03-06
print(Schoolware.agenda_week()) # Returns whole week agenda points
```

