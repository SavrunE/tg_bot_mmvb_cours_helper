import aiohttp

async def get_moex_price(ticker: str):
    url = f"https://iss.moex.com/iss/engines/stock/markets/shares/securities/{ticker}.json"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            data = await response.json()

    current_price, close_price = None, None

    columns = data['securities']['columns']
    for row in data['securities']['data']:
        if row[columns.index('BOARDID')] == 'TQBR':
            close_price = row[columns.index('PREVPRICE')]

    columns = data['marketdata']['columns']
    for row in data['marketdata']['data']:
        if row[columns.index('BOARDID')] == 'TQBR':
            current_price = row[columns.index('LAST')]

    if current_price is None or close_price is None:
        return None
    return [current_price, close_price]