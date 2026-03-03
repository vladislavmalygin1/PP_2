import re
import json

def parse_receipt(text):
    data = {
        "merchant": "EUROPHARMA",
        "date_time": "",
        "items": [],
        "total_amount": 0.0,
        "payment_method": ""
    }

    # 1. Extract Date and Time
    date_match = re.search(r"(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})", text)
    if date_match:
        data["date_time"] = date_match.group(1)

    # 2. Extract Payment Method
    payment_match = re.search(r"(Банковская карта|Наличные):", text)
    if payment_match:
        data["payment_method"] = payment_match.group(1)

    # 3. Extract Total
    total_match = re.search(r"ИТОГО:\s*([\d\s,]+)", text)
    if total_match:
        data["total_amount"] = float(total_match.group(1).replace(" ", "").replace(",", "."))

    # 4. Extract Products and Prices
    # Pattern: Digit + dot + newline + Name + newline + (qty x price) + newline + subtotal
    item_pattern = re.compile(
        r"\d+\.\n(.*?)\n\d+,\d+\s+x\s+[\d\s,]+\n([\d\s,]+)", 
        re.MULTILINE | re.DOTALL
    )
    
    matches = item_pattern.findall(text)
    for name, price_str in matches:
        clean_name = name.strip().replace("\n", " ")
        clean_price = float(price_str.replace(" ", "").replace(",", "."))
        data["items"].append({
            "product": clean_name,
            "price": clean_price
        })

    return data


with open("raw.txt", "r", encoding="utf-8") as f:
    content = f.read()
    parsed_json = parse_receipt(content)

print(json.dumps(parsed_json, indent=4, ensure_ascii=False))