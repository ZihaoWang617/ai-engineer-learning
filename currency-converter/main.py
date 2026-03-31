from src.models import ConversionRequest, ConversionResult
from src.converter import convert_currency
from rich.console import Console
from src.history import save_record, load_history

console = Console()
def main():
    print("This is a currency converter.")

    while True:
        choice = get_input("Enter 'h' to view history, 'q' to quit, or press Enter to continue: ").lower()
        if choice == 'h':
            history = load_history()
            if not history:
                console.print("No history found.")
            else:
                console.print("Conversion History:")
                for record in history:
                    console.print(f"{record['amount']} {record['base']} ->  {record['result']} {record['target']} at rate {record['rate']}", style ="bold cyan") 
            continue
        elif choice =='':
            pass
        else:
            print("Invalid choice. Please enter 'h', 'q', or press Enter to continue.")
            continue    
        base = get_valid_currency("Please enter your current currency (e.g., USD): ")
        target = get_valid_currency("Please enter the target currency (e.g., EUR): ")
        amount = get_valid_amount()
        request = ConversionRequest(amount=amount, base=base, target=target)
        result = convert_currency(request)
        if result is not None:
            save_record(result)
            display_result(result)
        else:
            console.print("Sorry, we couldn't fetch the exchange rate. Please check your currency codes and try again.", style="bold red")
        again = get_input("Continue? (y/n): ").lower()
        if again != "y":
            break

def get_input(prompt: str) -> str:
    value = input(prompt)
    if value.lower() == 'q':
        console.print("Good bye!", style="bold blue")
        exit()
    return value

def get_valid_currency(prompt: str) -> str:
    while True:
        code = get_input(prompt).upper()
        if code.isalpha() and len(code) == 3:
            return code
        else:
            console.print("Invalid currency code. Please enter a 3-letter currency code.", style="bold red")

def get_valid_amount() -> float:
    while True:
        try:
            amount = float(get_input("Please enter the amount you want to convert: "))
            return amount
        except ValueError:
            console.print("Invalid amount. Please enter a numeric value.", style="bold red")

def display_result(result: ConversionResult):
    console.print(f"{result.request.amount} {result.request.base} -> {result.converted_amount:.2f} {result.request.target} at an exchange rate of {result.rate:.4f}.", style="bold green")

if __name__ == "__main__":
    main()