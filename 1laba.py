from datetime import datetime

class FuelPrice:
    def __init__(self, fuel_type, date_obj, price_val):
        
        self.fuel_type = fuel_type
        self.date = date_obj
        self.price = price_val

    def __str__(self):
        
        return f"Объект: {self.fuel_type}, Дата: {self.date}, Цена: {self.price}"

def create_fuel_object(line):
    start_quote = line.find('"')
    end_quote = line.rfind('"')
    
    if start_quote == -1 or end_quote == -1 or start_quote == end_quote:
        raise ValueError("В строке должны быть кавычки для типа топлива")

    fuel_name = line[start_quote + 1 : end_quote]
    remaining_part = line[:start_quote] + " " + line[end_quote + 1:]
    
    parts = remaining_part.split()
    
    date_val = None
    price_val = None

    for p in parts:
        
        if "." in p and p.count(".") == 2 and len(p) == 10:
            date_val = datetime.strptime(p, "%Y.%m.%d").date()
        else:
            try:
                price_val = float(p)
            except ValueError:
                continue

    if not date_val or price_val is None:
        raise ValueError("Не найдены обязательные поля: Дата или Цена")

    
    return FuelPrice(fuel_name, date_val, price_val)


print("Введите данные (Пример: Топливо \"АИ-95\" 2026.02.25 95.05)")
print("Для выхода нажмите Enter в пустой строке.\n")

while True:
    user_input = input("Ввод: ").strip()
    if not user_input:
        break
    try:
        obj = create_fuel_object(user_input)
        print("Успех!", obj)
        print("-" * 30)
    except Exception as e:
        print(f"Ошибка: {e}")