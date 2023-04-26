<p align="center">
  <img src="https://user-images.githubusercontent.com/49933115/139837223-bf23d3a9-4638-4e17-994a-ac8678d5f517.png" width="150">
  &nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
  <img src="https://freelogopng.com/images/all_img/1681039084chatgpt-icon.png" width="150">
</p>
<p align="center">
  <b><a href="https://t.me/chatgpt_topic_bot/">@chatgpt_topic_bot</a></b>
</p>
Бот для Telegram, позволяющий использовать нейросеть ChatGPT от OpenAI в форумах (группы с темами).
Бот будет отвечать на любые сообщения в одном заданном топике форума.

## Оглавление

1. [Подключение к SSH через PuTTY на Windows](#-подключение-к-ssh-через-putty-на-windows)
    1. [Скачайте и установите PuTTY](#шаг-1-скачайте-и-установите-putty)
    2. [Сохраните сессию на подключение](#шаг-2-сохраните-сессию-на-подключение)
    3. [Подключитесь к серверу](#шаг-3-подключитесь-к-серверу)
    4. [Введите логин и пароль](#шаг-4-введите-логин-и-пароль)
2. [Установка и запуск (Ubuntu 22.04)](#-установка-и-запуск-ubuntu-2204)
    1. [Базовые пакеты](#1-базовые-пакеты)
    2. [Python 3.11](#2-python-311)
    3. [Запуск](#3-запуск)
3. [👮‍♀️ Права администратора](#%EF%B8%8F-права-администратора)
4. [💬 История сообщений](#-история-сообщений-логи)
# 🔌 Подключение к SSH через PuTTY на Windows

PuTTY - это клиент для протокола SSH, который может использоваться для удаленного управления устройствами через командную строку. При помощи PuTTY вы можете подключаться к серверу, используя SSH-ключи, логин и пароль от SSH.

### Шаг 1: Скачайте и установите PuTTY

Перейдите на официальный сайт PuTTY (https://www.chiark.greenend.org.uk/~sgtatham/putty/latest.html) и скачайте установочный файл для вашей операционной системы. После того, как скачивание будет завершено, запустите установочный файл и следуйте указаниям на экране для установки PuTTY.

### Шаг 2: Сохраните сессию на подключение

Откройте PuTTY и введите адрес сервера в поле "Host name". Выберите протокол "SSH" и порт "22" (если он отличается от стандартного). Дайте название вашей сессии в поле "Saved Sessions" и нажмите кнопку "Save". Это позволит вам сохранить настройки подключения для будущего использования.

### Шаг 3: Подключитесь к серверу

Выберите сохраненную ранее сессию и нажмите кнопку "Open". Вам будет предложено установить связь с сервером. Нажмите "Yes", чтобы подтвердить разрешение на подключение. 

### Шаг 4: Введите логин и пароль

После того, как вы успешно подключились к серверу, вам понадобится ввести логин и пароль от SSH, чтобы получить доступ. Наберите логин и нажмите Enter. После этого введите пароль и нажмите Enter.

После ввода логина и пароля вы получите удаленный доступ к серверу через SSH с использованием клиента PuTTY.

# 💿 Установка и запуск (Ubuntu 22.04)

### 1. Базовые пакеты
Для начала установим оболочку `fish` для замены `bash` для более удобного управления терминалом и screen, чтобы легко запускать бота в фоне.
`screen` обычно уже предустановлен в системе.
```
sudo apt update
sudo apt install fish screen
```
Сразу перейдем в `fish`. Для этого достаточно написать одно слово:
```
fish
```
### 2. Python 3.11
Установим Python версии 3.11:
```
sudo apt install software-properties-common -y
sudo add-apt-repository ppa:deadsnakes/ppa
```
Когда выйдет сообщение "`Press [ENTER] to continue or ctrl-c to cancel adding it`", нажмите Enter.</br>
После этого можно установить `python3.11` вместе с pip и venv с помощью `apt`:
```
sudo apt install python3.11 python3-pip python3.11-venv
```
### 3. Запуск
Копируем этот репозиторий (бота) в папку chatgpt-topic-bot по пути, в котором вы сейчас находитесь:
```
git clone https://diprog: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@github.com/diprog/chatgpt-topic-bot.git
```
Переходим в папку с ботом
```
cd chatgpt-topic-bot
```
Создаём виртуальное окружение:
```
python3.11 -m venv .venv
```
Активируем виртуальное окружение:
```
. .venv/bin/activate.fish
```
Устанавливаем требуемые зависимости:
```
pip install -U --pre aiogram
pip install jsonpickle
```
Запускаем бота:
```
screen -S chatgpt -L -d -m python main.py
```

# 👮‍♀️ Права администратора
* Только администраторы самого бота могут включать его в своих группах.
* Также они могут обращаться к нейросети внутри личного чата, а не только в группе.
### Управление правами
Сначала в `constants.py` задаются id разработчика бота и главного администратора с помощью переменных `DEVELOPER_ID` и `MAIN_ADMIN_ID` соответственно.</br>
Затем с помощью команды `/admin` в личных сообщениях с ботом пользователь может отправить запрос на получение прав администратора.

# 💬 История сообщений (логи)
Администратор может выбрать группу, которая будет использоваться для хранения историй сообщений всех пользователей бота.
### Выбор группы
* Советую создать пустую группу. Она должна быть супергруппой, и в ней должны быть включены темы.
* Затем, находясь в группе, нужно отправить команду /logging.
* Готово, теперь для каждого пользователя будут создаваться отдельные темы, где будут храниться истории общения с нейросетью.
