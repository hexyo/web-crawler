## Установка
#### 1. Скопировать проект
```
$ git clone https://github.com/klizzi/web-crawler.gitcd
$ cd web-crawler
```

#### 2. Запустить виртуальное окружение
```
$ \venv\scripts\activate
```

## Использование
### Загрузка страницы (load)
Принимает один параметр: url
Обходит сайт с глубиной 2 и записывает информацию в базу данных
Пример использования:
```
main.py load http://vesti.ru
>> Success! Now you can use `get url -n x`
>> execution time: xxx sec ||| peak memory usage: xx MiB
```
Если данный сайт уже записан в базу, то появится предложение обновить информацию:
```
main.py load http://vesti.ru
>>Page already was loaded to database. Wanna update it?'
>>y/n:
```

### Получение данных (get)
Принимает два параметра: url, -n (x)
Выводит n-нное количество url из пропарсенного сайта
Пример использования:
```
main.py get http://vesti.ru -n 3
>>https://vgtrk.com/: "ВГТРК"
>>https://russia.tv/: "Телеканал «Россия» / Смотреть онлайн / Видео / Телепрограмма, кино, сериалы, шоу"
>>https://www.vesti.ru/: "Вести.Ru: новости, видео и фото дня"
```

### Удаление всех данных из базы (clear)
Не принимает параметров
Удаляет всю информацию, записанную в бд.
Пример использования:
```
main.py clear
>> Are you sure want DELETE ALL DATA
>> y/n:
```
