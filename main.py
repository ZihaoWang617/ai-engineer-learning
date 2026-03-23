import requests
from rich.console import Console
from rich.table import Table

console = Console()

def get_exchange_rate(base: str, target: str):
    """调用免费汇率API，获取实时汇率"""
    url = f"https://open.er-api.com/v6/latest/{base}"
    response = requests.get(url)
    data = response.json()
    
    if data["result"] == "success":
        rate = data["rates"][target]
        return rate
    else:
        return None

# 获取几个常用汇率
pairs = [("USD", "CNY"), ("USD", "CAD"), ("CAD", "CNY")]

table = Table(title="实时汇率")
table.add_column("From", style="cyan")
table.add_column("To", style="green")
table.add_column("Rate", style="yellow")

for base, target in pairs:
    rate = get_exchange_rate(base, target)
    if rate:
        table.add_row(base, target, str(rate))
    else:
        table.add_row(base, target, "获取失败")

console.print(table)