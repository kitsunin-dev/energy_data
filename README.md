# Обработка данных плановых работ на электрических сетях в СПб
Программа совершает следующие действия:
1. берет данные из таблиц графика плановых работ на электрических сетях на страницах сайта Россетей (за неделю вперед от сегодняшнего дня);
2. парсит хранящиеся в таблице адреса домов;
3. создает запросы к API Геокода и получает от него доп. информацию об адресе;
4. выгружает результаты в базу данных (использовалась СУБД PostgreSQL);
5. автоматически производит вышеуказанные процедуры согласно настроенному расписанию.
6. визуализирует координаты домов на графике в виде точек;

Репозиторий состоит из трех файлов:
- *iac.py*: файл скрипта, делает все, кроме визуализации;
- *visual.ipynb*: блокнот, получает данные из БД и визуализирует в виде точек на графике;
- *README.md*: описание программы и репозитория.

**Внимание!** Скрипт может работать довольно долго (до 10 минут) ввиду большого объема данных и частых запросов к API и БД.
