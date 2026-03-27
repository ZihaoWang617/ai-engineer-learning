from src.models import ConversionRequest
from src.converter import convert_currency
from rich.console import Console

console = Console()
def main():
    print("This is a currency converter.")
    while True:
        base = input("Please enter your current currency (e.g., USD): ").upper()
        if not base.isalpha() or len(base) != 3:
            print("Invalid currency code.Please enter a 3-letter currency code.")
            continue
        target = input("Please enter the target currency (e.g., EUR): ").upper()
        if not target.isalpha() or len(target) != 3:
            print("Invalid currency code. Please enter a 3-letter currency code.")
            continue
        try:
            amount = float(input("Please enter the amount you want to convert: "))
        except ValueError:
            console.print("Invalid amount. Please enter a numeric value.")
            continue

        request = ConversionRequest(amount=amount, base=base, target=target)
        result = convert_currency(request)
        if result is not None:
            console.print(f"{result.request.amount} {result.request.base} is equal to {result.converted_amount:.2f} {result.request.target} at an exchange rate of {result.rate:.4f}.", style="bold green")
        else:
            console.print("Sorry, we couldn't fetch the exchange rate. Please check your currency codes and try again.", style="bold red")

        again = input("Continue? (y/n): ").lower()
        if again != "y":
            break

if __name__ == "__main__":
    main()