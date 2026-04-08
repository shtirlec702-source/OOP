import unittest
import tempfile
import os
from datetime import date
from model import CurrencyModel, ParseError

class TestCurrencyModel(unittest.TestCase):
    def setUp(self):
        """Создает свежую модель перед каждым тестом."""
        self.model = CurrencyModel()

    def test_parse_valid_line(self):
        """Тест парсинга корректной строки."""
        line = 'Курс "USD" "RUB" 75.5 2026.02.25'
        rate = self.model.parse_line(line)
        
        self.assertEqual(rate.currency_from, "USD")
        self.assertEqual(rate.currency_to, "RUB")
        self.assertEqual(rate.rate, 75.5)
        self.assertEqual(rate.date, date(2026, 2, 25))

    def test_parse_missing_quotes(self):
        """Тест: отсутствие необходимых кавычек для валют вызывает ParseError."""
        line = 'Курс USD "RUB" 75.5 2026.02.25'
        with self.assertRaises(ParseError):
            self.model.parse_line(line)

    def test_parse_missing_date(self):
        """Тест: отсутствие правильной даты вызывает ParseError."""
        line = 'Курс "USD" "RUB" 75.5 2026-02-25' # Неверный формат даты
        with self.assertRaises(ParseError):
            self.model.parse_line(line)

    def test_parse_missing_rate(self):
        """Тест: отсутствие числа вызывает ParseError."""
        line = 'Курс "USD" "RUB" abc 2026.02.25'
        with self.assertRaises(ParseError):
            self.model.parse_line(line)

    def test_load_from_file_with_errors(self):
        """Тест загрузки из файла: валидные читаются, невалидные пропускаются."""
        file_content = (
            'Курс "USD" "RUB" 75.5 2026.02.25\n'
            'Плохая строка без кавычек и дат\n'
            'Еще одна "EUR" "RUB" 85.0 2026.03.01\n'
            'Тут нет курса "GBP" "RUB" 2026.04.01\n'
        )
        
        # Создаем временный файл
        fd, filepath = tempfile.mkstemp(text=True)
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write(file_content)

        try:
            # Загружаем файл через модель. Ожидаем, что загрузятся 2 из 4.
            success_count = self.model.load_from_file(filepath)
            
            self.assertEqual(success_count, 2)
            self.assertEqual(len(self.model.rates), 2)
            self.assertEqual(self.model.rates[0].currency_from, "USD")
            self.assertEqual(self.model.rates[1].currency_from, "EUR")
        finally:
            # Удаляем временный файл
            os.remove(filepath)

if __name__ == '__main__':
    unittest.main()