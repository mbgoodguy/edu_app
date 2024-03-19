# Приложение образовательной платформы


## Запуск
- `docker-compose -f docker-compose-local.yaml up -d` - запуск PostgreSQL

> Если возникает ошибка ` Error starting userland proxy: listen tcp4 0.0.0.0:5432: bind: address already in use`
то освобождаем локальный порт 5432 (скорее всего занят сервисом postgresql, освобождаем командой 
`sudo systemctl stop postgresql`) или меняем порт в docker-compose-local.yaml

