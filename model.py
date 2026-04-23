import re
import logging
from datetime import datetime, date  

logging.basicConfig(
    filename='errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class ParseError(Exception):
    def __init__(self, message):
        super().__init__(message)
        logging.warning(f"Ошибка парсинга: {message}")


# ═══════════════════════════════════════════════════════════════════════
# БАЗОВЫЙ КЛАСС (Курс валюты)
# ═══════════════════════════════════════════════════════════════════════
class CurrencyRate:
    """Класс для хранения информации об одном курсе валюты."""
    def __init__(self, currency_from: str, currency_to: str, rate: float, rate_date: datetime.date | None):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.rate = rate
        self.date = rate_date

    def __str__(self) -> str:
        return f"Курс: {self.currency_from} = {self.rate} {self.currency_to} (Дата: {self.date})"

    # ПОЛИМОРФИЗМ: Метод для получения данных строки в GUI
    def to_row(self) -> tuple:
        date_str = self.date.strftime("%Y.%m.%d") if self.date else ""
        return ("Курс", self.currency_from, self.currency_to, self.rate, date_str)

    # ПОЛИМОРФИЗМ: Метод для сохранения записи в файл
    def to_save_string(self) -> str:
        date_str = self.date.strftime("%Y.%m.%d") if self.date else ""
        return f'"{self.currency_from}" "{self.currency_to}" {self.rate} {date_str}'


# ═══════════════════════════════════════════════════════════════════════
# ДОЧЕРНИЙ КЛАСС (Person наследует CurrencyRate)
# ═══════════════════════════════════════════════════════════════════════
class Person(CurrencyRate):
    """Класс для хранения персоны. Наследует структуру CurrencyRate для полиморфизма."""
    def __init__(self, name: str, country: str, money: float):
        # Инициализируем родителя. Маппинг: Откуда=Имя, Куда=Страна, Курс=Деньги, Дата=None
        super().__init__(currency_from=name, currency_to=country, rate=money, rate_date=None)
        
        # Сохраняем собственные атрибуты для логики REM (поиск по name, country, money)
        self.name = name
        self.country = country
        self.money = money

    def __str__(self) -> str:
        return f"Человек: {self.name}, {self.country}, {self.money}"

    # ПОЛИМОРФИЗМ: Переопределение метода для GUI
    def to_row(self) -> tuple:
        return ("Персона", self.name, self.country, self.money, "—")

    # ПОЛИМОРФИЗМ: Переопределение метода для сохранения
    def to_save_string(self) -> str:
        return f'{self.name},{self.country},{self.money}'


# ═══════════════════════════════════════════════════════════════════════
# МОДЕЛЬ
# ═══════════════════════════════════════════════════════════════════════
class CurrencyModel:
    """Класс, управляющий единым списком записей (полиморфизм)."""
    def __init__(self):
        # Единый список для объектов CurrencyRate и его наследника Person
        self.records: list[CurrencyRate] = []

    def parse_line(self, line: str) -> CurrencyRate:
        line = line.strip()
        if not line:
            raise ParseError("Пустая строка")

        currencies = re.findall(r'"([^"]+)"', line)
        if len(currencies) < 2:
            raise ParseError(f"Не найдено две валюты в кавычках в строке: '{line}'")
        curr_from, curr_to = currencies[0], currencies[1]

        remaining_line = re.sub(r'"[^"]+"', '', line).split()

        rate_val = None
        date_val = None

        for part in remaining_line:
            if part.count('.') == 2:
                try:
                    date_val = datetime.strptime(part, "%Y.%m.%d").date()
                except ValueError:
                    pass
            else:
                try:
                    rate_val = float(part)
                except ValueError:
                    pass

        if date_val is None:
            raise ParseError(f"Не найдена корректная дата (гггг.мм.дд) в строке: '{line}'")
        if rate_val is None:
            raise ParseError(f"Не найден числовой курс в строке: '{line}'")

        return CurrencyRate(curr_from, curr_to, rate_val, date_val)

    def load_from_file(self, filepath: str) -> int:
        success_count = 0
        with open(filepath, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line: continue
                try:
                    rate = self.parse_line(line)
                    self.records.append(rate)
                    success_count += 1
                except ParseError:
                    pass
        return success_count

    def add_record(self, line: str):
        rate = self.parse_line(line)
        self.records.append(rate)

    def delete_records(self, indices: list[int]):
        """Удаляет записи из единого списка по индексам."""
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.records):
                self.records.pop(index)

    def parse_csv_line(self, csv_line: str) -> CurrencyRate:
        parts = [p.strip().strip('"').strip("'") for p in csv_line.split(',')]
        if len(parts) < 4:
            raise ParseError(f"Недостаточно полей в CSV строке: '{csv_line}'")
        curr_from, curr_to = parts[0], parts[1]
        if not curr_from or not curr_to:
            raise ParseError(f"Пустое название валюты: '{csv_line}'")
        try:
            rate_val = float(parts[2])
            date_val = datetime.strptime(parts[3], "%Y.%m.%d").date()
        except ValueError as e:
            raise ParseError(f"Ошибка значений в CSV: {e}")
        return CurrencyRate(curr_from, curr_to, rate_val, date_val)

    def parse_person_csv(self, csv_line: str) -> Person:
        parts = [p.strip().strip('"').strip("'") for p in csv_line.split(',')]
        if len(parts) < 3:
            raise ParseError(f"Недостаточно полей для Person: '{csv_line}'")
        name, country = parts[0], parts[1]
        if not name or not country:
            raise ParseError(f"Пустое имя или страна: '{csv_line}'")
        try:
            money = float(parts[2])
        except ValueError:
            raise ParseError(f"Некорректная сумма '{parts[2]}'")
        return Person(name, country, money)

    def save_to_file(self, filepath: str) -> int:
        """Полиморфное сохранение: вызывается переопределенный метод to_save_string()"""
        with open(filepath, 'w', encoding='utf-8') as f:
            for record in self.records:
                f.write(record.to_save_string() + '\n')
        return len(self.records)

    # ─────────────────────────────────────────────────────────────────
    # Универсальное удаление REM
    # ─────────────────────────────────────────────────────────────────
    _RATE_FIELDS   = {'rate', 'currency_from', 'currency_to', 'date'}
    _PERSON_FIELDS = {'money', 'country', 'name'}
    _SUPPORTED_FIELDS = _RATE_FIELDS | _PERSON_FIELDS
    _SUPPORTED_OPS = ('==', '!=', '<=', '>=', '<', '>')

    def _match_condition(self, record: CurrencyRate, field: str, op: str, value_str: str) -> bool:
        """Универсальная проверка условия с учетом типа объекта."""
        is_person = isinstance(record, Person)
        if is_person and field not in self._PERSON_FIELDS: return False
        if not is_person and field not in self._RATE_FIELDS: return False

        if not hasattr(record, field):
            return False

        actual = getattr(record, field)
        if actual is None: return False # Для дат у персон
        
        value_str = value_str.strip().strip('"').strip("'")

        try:
            if isinstance(actual, (float, int)):
                val = float(value_str)
            elif isinstance(actual, date): # Теперь работает правильно
                val = datetime.strptime(value_str, "%Y.%m.%d").date()
            else:
                val = value_str
        except (ValueError, TypeError):
            return False

        if isinstance(actual, str) and op not in ('==', '!='):
            return False

        try:
            if op == '<':  return actual < val
            if op == '>':  return actual > val
            if op == '==': return actual == val
            if op == '<=': return actual <= val
            if op == '>=': return actual >= val
            if op == '!=': return actual != val
        except:
            return False
        return False
    def remove_by_condition(self, condition: str) -> int:
        condition = condition.strip()
        field = op_used = value_str = None
        for op in self._SUPPORTED_OPS:
            if op in condition:
                parts = condition.split(op, 1)
                field_candidate = parts[0].strip()
                if field_candidate in self._SUPPORTED_FIELDS:
                    field, op_used, value_str = field_candidate, op, parts[1].strip()
                    break

        if not field:
            raise ParseError(f"Некорректное условие REM: '{condition}'.")

        before = len(self.records)
        self.records = [rec for rec in self.records if not self._match_condition(rec, field, op_used, value_str)]
        return before - len(self.records)

    def execute_commands_from_file(self, filepath: str) -> dict:
        stats = {'add': 0, 'rem': 0, 'save': 0, 'errors': 0}
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, raw_line in enumerate(f, 1):
                line = raw_line.strip()
                if not line or line.startswith('#'): continue

                upper = line.upper()
                if upper.startswith('ADD '):
                    csv_data = line[4:].strip()
                    field_count = len(csv_data.split(','))
                    try:
                        # Полиморфное добавление в единый список
                        if field_count >= 4:
                            obj = self.parse_csv_line(csv_data)
                        else:
                            obj = self.parse_person_csv(csv_data)
                        self.records.append(obj)
                        stats['add'] += 1
                    except ParseError as e:
                        stats['errors'] += 1
                        logging.warning(f"[CMD строка {line_num}] ADD: {e}")

                elif upper.startswith('REM '):
                    try:
                        stats['rem'] += self.remove_by_condition(line[4:].strip())
                    except ParseError as e:
                        stats['errors'] += 1
                        logging.warning(f"[CMD строка {line_num}] REM: {e}")

                elif upper.startswith('SAVE '):
                    try:
                        self.save_to_file(line[5:].strip())
                        stats['save'] += 1
                    except OSError as e:
                        stats['errors'] += 1
                        logging.warning(f"[CMD строка {line_num}] SAVE: {e}")
                else:
                    stats['errors'] += 1
        return stats