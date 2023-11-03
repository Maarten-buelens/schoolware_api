
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
| bot_token | telegram bot token to enable telegram bot
| chat_id | id to send messages to
| verbose | show a some more info
| debug | show a some more info

## Install
* `pip3 install schoolware_api --upgrade `
* `playwright install &&  playwright install-deps`

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
```
## Complete example
```python
from schoolware_api import schoolware
config = {"domain":"","password":"","user":"","schoolware_login": "false","verbose": false, "bg": true, "bot_token": "", "chat_id": ""}

Schoolware = schoolware(config)

# same as other
```
