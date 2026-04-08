import re
import logging
from datetime import datetime

# Настройка логирования: некорректные строки будут записываться в файл errors.log
logging.basicConfig(
    filename='errors.log',
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    encoding='utf-8'
)

class ParseError(Exception):
    """Пользовательское исключение для ошибок парсинга строки валют."""
    pass

class CurrencyRate:
    """Класс для хранения информации об одном курсе валюты."""
    def __init__(self, currency_from: str, currency_to: str, rate: float, rate_date: datetime.date):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.rate = rate
        self.date = rate_date

    def __str__(self) -> str:
        return f"Курс: {self.currency_from} = {self.rate} {self.currency_to} (Дата: {self.date})"

class CurrencyModel:
    """Модель, управляющая списком курсов и бизнес-логикой."""
    def __init__(self):
        self.rates: list[CurrencyRate] = []

    def parse_line(self, line: str) -> CurrencyRate:
        """Парсит строку и возвращает объект CurrencyRate. Выбрасывает ParseError при ошибке."""
        line = line.strip()
        if not line:
            raise ParseError("Пустая строка")

        # 1. Извлекаем валюты
        currencies = re.findall(r'"([^"]+)"', line)
        if len(currencies) < 2:
            raise ParseError(f"Не найдено две валюты в кавычках в строке: '{line}'")
        curr_from, curr_to = currencies[0], currencies[1]

        # 2. Очищаем строку от валют для поиска чисел и дат
        remaining_line = re.sub(r'"[^"]+"', '', line).split()

        # 3. Извлекаем дату и курс
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
        """
        Читает файл построчно. Корректные строки добавляет, 
        некорректные пропускает и пишет в лог.
        Возвращает количество успешно добавленных записей.
        """
        success_count = 0
        with open(filepath, 'r', encoding='utf-8') as file:
            for line_num, line in enumerate(file, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    rate = self.parse_line(line)
                    self.rates.append(rate)
                    success_count += 1
                except ParseError as e:
                    # Логируем ошибку, программа продолжает работу
                    logging.warning(f"Ошибка в строке {line_num}: {e}")
        return success_count

    def add_record(self, line: str):
        """Добавляет одну запись из строки."""
        rate = self.parse_line(line)
        self.rates.append(rate)

    def delete_records(self, indices: list[int]):
        """Удаляет записи по списку индексов (удаление с конца, чтобы не сбить индексы)."""
        for index in sorted(indices, reverse=True):
            if 0 <= index < len(self.rates):
                self.rates.pop(index)