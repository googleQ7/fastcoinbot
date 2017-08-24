# Fastcoin-Бот
Это краткая документация по боту.

## Как запустить бота
### Настройка окружение
Создайте `.env` файл в папке с ботом и откройте его в текстовом редакторе.
Заполните его следующим образом:
```
export BOT_TOKEN=172195613:BBFxbrBuVxPFj6ckKIqPraLv81c19Rad34Q
export WEBHOOK_URL=webhook.example.com
export PRIVATE_KEY=0e37e5feb349ce0c8е03963ddd4163b19k171b0be9ad1c7a7fe266edaedcf3
export ADMIN=205279061
export CARD_NUMBER="1231 213 1233 1323"
```

1) Токен бота, который вы болучается от BotFather
2) URL вебхука на который будут приходить сообщения [см. документацию BOT API](https://core.telegram.org/bots/api#setwebhook)
3) Приватный ключ от главного Bitcoin-кошелька, [см. документация Bitcoin](https://en.bitcoin.it/Private_key)
4) Telegram-Id администратора, можно получить в [@myidbot](https://t.me/myidbot)
5) Номер Сбербанк-карты для перевода
