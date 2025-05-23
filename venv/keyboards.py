from aiogram import types

moex_tickers = [
    'AFLT', 'ALRS', 'CHMF', 'FEES', 'GAZP', 'GMKN', 'HYDR',
    'IRAO', 'MAGN', 'MTLRP', 'MTSS', 'NLMK', 'NVTK', 'OGKB', 'PLZL', 'RASP',
    'ROSN', 'RUAL', 'RTKM', 'SBER', 'SIBN', 'SNGSP', 'TATN',
    'VTBR', 'YDEX'
]

async def get_main_keyboard() -> types.InlineKeyboardMarkup:
    moex_buttons = [
        [types.InlineKeyboardButton(text=ticker, callback_data=f"moex_course:{ticker}")
         for ticker in moex_tickers[i:i + 3]]
        for i in range(0, len(moex_tickers), 3)
    ]

    # crypto_buttons = [[
    #     types.InlineKeyboardButton(text="BTC", callback_data="crypto_course:btc"),
    #     types.InlineKeyboardButton(text="ETH", callback_data="crypto_course:eth")
    # ]]

    return types.InlineKeyboardMarkup(inline_keyboard= moex_buttons)
    # return types.InlineKeyboardMarkup(inline_keyboard=crypto_buttons + moex_buttons)