import datetime
import requests
import asyncio
import aiohttp

from aiogram import Bot, Dispatcher, types, F

Bot_Token = "7600224844:AAHKPuIOLO3NzEu2y52MFO7ot0zSRIY9ZF8" #@IgorTestBotbot
# Bot_Token = "7659072923:AAGxsh9FvWXf7l0wR4cF390ZSrqbMaLCv0g" #@testIgobotbot


bot = Bot(Bot_Token)
dp = Dispatcher()


@dp.message(F.text == "/start")
async def user_start_bot(message: types.Message):
    await message.answer(
        f"Привет {message.from_user.first_name}\n"
        "Этот бот покажет тебе актуальную цену актива MMVB и цену его закрытия.",
        reply_markup=types.InlineKeyboardMarkup(
            inline_keyboard=[
                [types.InlineKeyboardButton(text="BTC", callback_data="crypto_course:btc"),
                types.InlineKeyboardButton(text="ETH", callback_data="crypto_course:eth"),
                types.InlineKeyboardButton(text="SBER", callback_data="moex_course:SBER")],
            ]
        )
    )

@dp.callback_query(F.data.startswith("crypto_course:"))
async def crypto_course(callback_data: types.CallbackQuery):
    crypto = callback_data.data.split(":")[-1]
    price = await get_crypto_currency(crypto)
    if price:
        await callback_data.message.answer(
            f"Курс {crypto.upper()} на {datetime.datetime.now().date().strftime("%d-%m-%Y")} равен: {price[0]} RUB или {price[1]} USD"
        )
    else:
        await callback_data.message.answer(
            "Ошибка при получении валюты, попробуйте снова позднее."
        )
    await callback_data.answer()

async def get_crypto_currency(token: str) -> [float,float] :
    url = "https://api.cryptapi.io/" + token + "/info/"
    query = {"prices": "1"}
    # response = requests.get(url, params=query) #работает синхронно, нужно переделать на асинхрон
    response = await fetch_data(url, query)

    if response:
        data = response
        price_rub = data.get("prices", {}).get("RUB")
        price_usd = data.get("prices", {}).get("USD")
        return  [round(float(price_rub),2),round(float(price_usd),2)]
    else:
        return None

async def fetch_data(url, query):
    async with aiohttp.ClientSession() as session:
        async with session.get(url, params=query) as response:
            return await response.json()

@dp.callback_query(F.data.startswith("moex_course:"))
async def get_moex_price(callback_data: types.CallbackQuery):
    ticker = callback_data.data.split(":")[-1]
    url = f'https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}.json'
    response = requests.get(url)
    data = response.json()

    try:
        market_data = data['marketdata']['data'][0]
        price_index = data['marketdata']['columns'].index('LAST')

        await callback_data.message.answer(
            f"Курс {ticker} на {datetime.datetime.now().date().strftime("%d-%m-%Y")} равен: {market_data[price_index]} RUB "
        )
    except Exception as e:
        print("Ошибка при получении данных:", e)
        return None
    await callback_data.answer()


async def main():
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')