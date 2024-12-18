const { Telegraf } = require('telegraf');
const express = require('express');
const app = express();

// Замените на токен вашего бота
const bot = new Telegraf('7647826971:AAFy_OfXn5yWAiqyQ5A8_EmhUDjDhTYnp3M');

// Команда /start
bot.start((ctx) => ctx.reply('Привет! Я ваш бот для оформления заказов.'));

// Пример команды для отправки заказа
bot.command('order', (ctx) => {
    const orderDetails = "Ваш заказ:\n1. Пицца — 2 шт. — 1000₽\n2. Сок — 1 шт. — 200₽\n\nИтого: 1200₽";
    ctx.reply(`Спасибо за ваш заказ! Детали:\n\n${orderDetails}`);
});

// Ловим текстовые сообщения
bot.on('text', (ctx) => {
    ctx.reply(`Вы отправили: "${ctx.message.text}".`);
});

// Настраиваем webhook для Vercel
bot.telegram.setWebhook(`https://your-vercel-app.vercel.app/api`);
app.use(bot.webhookCallback('/api'));

// Экспортируем сервер для Vercel
module.exports = app;
