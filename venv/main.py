import datetime
import asyncio
import aiohttp
import tokens
import price_checker
import keyboards

from aiogram import Bot, Dispatcher, types, F

Bot_Token = tokens.load_token("Trade_helperbot")
# Bot_Token = tokens.load_token("IgorTestBotbot") #@IgorTestBotbot
# @testIgobotbot

bot = Bot(Bot_Token)
dp = Dispatcher()

async def on_startup():
    global session
    session = aiohttp.ClientSession()

async def on_shutdown():
    await session.close()

@dp.message(F.text.regexp(r"^[A-Za-z0-9]+$"))
async def handle_ticker_query(message: types.Message):
    ticker = message.text.strip().upper()
    await process_moex_ticker(message, ticker)

@dp.message(F.text == "/start")
async def user_start_bot(message: types.Message):
    await message.answer(
        f"Привет {message.from_user.first_name}!\n"
        "Этот бот покажет тебе актуальную цену любого из нижеприведенных активов и сравнит с ценой закрытия предыдущего дня.\n\n"
        "Так-же ты можешь написать любой индекс moex в чат (Пример `sber`) и получить результат.",
        parse_mode="Markdown",
        reply_markup = await keyboards.get_main_keyboard()
    )

@dp.callback_query(F.data.startswith("crypto_course:"))
async def crypto_course(callback_data: types.CallbackQuery):
    crypto = callback_data.data.split(":")[-1]
    price = await get_crypto_currency(crypto)
    if price:
        date_str = datetime.datetime.now().date().strftime("%d-%m-%Y")
        await callback_data.message.answer(
            f"Курс {crypto.upper()} на {date_str} равен: {price[0]} RUB или {price[1]} USD"
        )
    else:
        await callback_data.message.answer(
            "Ошибка при получении валюты, попробуйте снова позднее."
        )
    await callback_data.answer()

async def get_crypto_currency(token: str) -> [float,float] :
    url = "https://api.cryptapi.io/" + token + "/info/"
    query = {"prices": "1"}
    response = await fetch_data(url, query)

    if response:
        data = response
        price_rub = data.get("prices", {}).get("RUB")
        price_usd = data.get("prices", {}).get("USD")
        return  [round(float(price_rub),2),round(float(price_usd),2)]
    else:
        return None

async def fetch_data(url, query):
    try:
        async with session.get(url, params=query, timeout=10) as response:
            if response.status != 200:
                return None
            return await response.json()
    except Exception as e:
        print(f"Ошибка запроса к {url}: {e}")
        return None

@dp.callback_query(F.data.startswith("moex_course:"))
async def get_moex_price_callback(callback: types.CallbackQuery):
    ticker = callback.data.split(":")[-1]
    await process_moex_ticker(callback.message, ticker)
    await callback.answer()

# @dp.callback_query(F.data.startswith("moex_course:"))
# async def get_moex_price(callback_data: types.CallbackQuery):
#     ticker = callback_data.data.split(":")[-1]
#
#     try:
#         price = await price_checker.get_moex_price(ticker)
#         difference_price = price[0] - price[1]
#         formatted_diff = f"{difference_price:.8f}".rstrip('0').rstrip('.')
#         # difference_price = round(price[0] - price[1], 2)
#
#         date_str = datetime.datetime.now().date().strftime("%d-%m-%Y")
#         await callback_data.message.answer(
#             f"Курс {ticker} на {date_str}:\n"
#             f"Текущая цена: `{price[0]}` RUB\n"
#             f"Цена закрытия: `{price[1]}` RUB\n"
#             f"Разница: *{formatted_diff}* RUB", parse_mode="Markdown"
#         )
#     except Exception as e:
#         print("Ошибка при получении данных:", e)
#         return None
#     await callback_data.answer()

async def process_moex_ticker(message: types.Message, ticker: str):
    try:
        price = await price_checker.get_moex_price(ticker)

        if price is None or price[0] is None or price[1] is None:
            await message.answer(f"❌ Данные по тикеру `{ticker}` не найдены.", parse_mode="Markdown")
            return

        current, close = price
        diff = current - close
        formatted_diff = f"{diff:.8f}".rstrip('0').rstrip('.')

        date_str = datetime.datetime.now().date().strftime("%d-%m-%Y")
        await message.answer(
            f"Курс `{ticker}` на {date_str}:\n"
            f"Текущая цена: `{current}` RUB\n"
            f"Цена закрытия: `{close}` RUB\n"
            f"Разница: *{formatted_diff}* RUB", parse_mode="Markdown"
        )
    except Exception as e:
        print("Ошибка при получении данных:", e)
        await message.answer("⚠️ Произошла ошибка при получении данных.")

async def main():
    await on_startup()
    try:
        await dp.start_polling(bot)
    finally:
        await on_shutdown()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен')