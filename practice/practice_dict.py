currencies = {
    "USD": {"name": "US DOllar", "symbol": "$", "popular_pairs": ["EUR", "CNY", "CAD"]},
    "CNY": {"name": "Chinese Yuan", "symbol": "¥", "popular_pairs": ["USD", "EUR", "JPY"]},
    "CAD": {"name": "Canadian Dollar", "symbol": "C$", "popular_pairs": ["USD", "EUR", "CNY"]}
}
for code, info in currencies.items():
    print(f"{code}: {info['name']}, {info['symbol']}")
currencies_dict = {code: len(info["popular_pairs"]) for code, info in currencies.items()}
print(currencies_dict)
currencies.setdefault("JPY", {"name": "Japanese Yen", "symbol": "¥", "popular_pairs": ["USD", "EUR", "CNY"]})
print(currencies["JPY"])
currencies["USD"].update({"symbol": "US$"})
print(currencies["USD"]["symbol"])