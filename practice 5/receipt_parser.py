import re
import json

def parse_receipt(file_path):
    # Open
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()

    # Date
    date_match = re.search(r'Время:\s*(\d{2}\.\d{2}\.\d{4}\s\d{2}:\d{2}:\d{2})', text)
    date_time = date_match.group(1) if date_match else ""

    # Payment
    pay_match = re.search(r'(Банковская карта|Наличные):', text)
    payment_method = pay_match.group(1) if pay_match else ""

    # Total
    total_match = re.search(r'ИТОГО:\n([0-9\s,]+)', text)
    total_amount = total_match.group(1).strip() if total_match else ""

    # All prices
    all_prices = re.findall(r'\b\d{1,3}(?:\s\d{3})*,\d{2}\b', text)

    # Items
    pattern = r'\d+\.\n(.*?)\n([0-9,]+)\s*x\s*([0-9\s,]+)\n([0-9\s,]+)\nСтоимость'
    items_matches = re.findall(pattern, text)

    products = []
    calc_total = 0.0

    for m in items_matches:
        raw_price = m[3].replace(' ', '').replace(',', '.')
        calc_total += float(raw_price)
        
        products.append({
            "name": m[0].strip(),
            "qty": m[1].strip(),
            "price": m[2].strip(),
            "sum": m[3].strip()
        })

    # Result
    data = {
        "date": date_time,
        "method": payment_method,
        "total_text": total_amount,
        "total_calc": calc_total,
        "all_prices": all_prices,
        "items": products
    }

    # Print
    print(json.dumps(data, ensure_ascii=False, indent=2))

    # Save
    with open('output.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    parse_receipt('raw.txt')