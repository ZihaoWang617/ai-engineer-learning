# Currency-converter
A command-line currency converter that fetches real-time exchange rates and supports conversion history.
## Features
- Real-time exchange rate conversion using open.er-api.com
- Input validation for currency codes and amounts
- Conversion history saved to local JSON file
- History filtering by base or target currency
- Quit anytime by entering 'q'
## Project Structure
```
currency-converter/
|--src/
|   ├──models.py          -Data models (ConversionRequest, ConversionResult)
|   ├──api.py             -Exchange rate API integration
|   ├──converter.py       -Core conversion logic
|   └──history.py         -History management with JSON persistence
└──main.py                -CLI Entry point
```
## How to run
```bash
cd currency-converter
pip install -r ../requirements.txt
python3 main.py
```
## Tech Stack
- Python 3.9
- Requests (HTTP client)
- Rich (terminal formatting)
- Open Exchange Rate API