import json


with open("test.txt","w") as f:
    f.write("Hello World")
    f.write("\nThis is Zihao")
    f.write("\nI am learning you right now")

with open("test.txt","r") as f:
    print(f.read())

with open("test.txt","a") as f:
    f.write("\nThis is the end of the file")

records = [{"base": "USD", "target": "CNY", "amount": 100, "result": 691.61, "rate": 6.9161},
        {"base": "CAD", "target": "CNY", "amount": 50, "result": 250.29, "rate": 5.0057},
        {"base": "USD", "target": "EUR", "amount": 200, "result": 172.76, "rate": 0.8638}
]
with open("history.json", "w") as f:
    json.dump(records, f, indent=4)

with open("history.json", "r") as f:
    data= json.load(f)
    for data in data:
        print(f"{data['amount']} {data['base']} -> {data['result']} {data['target']}")