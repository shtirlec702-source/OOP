from datetime import datetime

class CurrencyRate:
    def __init__(self, currency_from, currency_to, rate, rate_date):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.rate = rate
        self.date = rate_date

    def __str__(self):
        return f"Курс: {self.currency_from} = {self.rate} {self.currency_to} (Дата: {self.date})"

def parse_currency_string(line):
    found_strings = []
    temp_line = line
    
    while '"' in temp_line:
        start = temp_line.find('"')
        end = temp_line.find('"', start + 1)
        if start != -1 and end != -1:
            found_strings.append(temp_line[start + 1 : end])
            temp_line = temp_line[:start] + " " + temp_line[end + 1:]
        else:
            break

    if len(found_strings) < 2:
        raise ValueError("Нужно указать две валюты в кавычках, например: \"USD\" \"RUB\"")

    remaining_parts = temp_line.split()
    
    rate_val = None
    date_val = None

    for part in remaining_parts:
        if "." in part and part.count(".") == 2:
            try:
                date_val = datetime.strptime(part, "%Y.%m.%d").date()
            except:
                continue
        else:
            try:
                rate_val = float(part)
            except ValueError:
                continue

    if rate_val is None or date_val is None:
        raise ValueError("Не найден курс или дата (гггг.мм.дд)")

    return CurrencyRate(found_strings[0], found_strings[1], rate_val, date_val)


print("Введите данные. Формат: Курс \"Валюта1\" \"Валюта2\" 75.5 2026.02.25")
while True:
    user_input = input("\nВвод: ").strip()
    if not user_input: break
    try:
        obj = parse_currency_string(user_input)
        print("Объект создан успешно!")
        print(obj)
    except Exception as e:
        print(f"Ошибка: {e}")