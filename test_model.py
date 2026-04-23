import unittest
import tempfile
import os
from datetime import date
from model import CurrencyModel, CurrencyRate, Person, ParseError

def make_rate(curr_from="USD", curr_to="RUB", rate=75.0, d=date(2026, 2, 25)) -> CurrencyRate:
    return CurrencyRate(curr_from, curr_to, rate, d)

def write_tmp(content: str, suffix=".txt") -> str:
    fd, path = tempfile.mkstemp(suffix=suffix, text=True)
    with os.fdopen(fd, 'w', encoding='utf-8') as f:
        f.write(content)
    return path


class TestParseLine(unittest.TestCase):
    def setUp(self): self.model = CurrencyModel()

    def test_valid_line(self):
        rate = self.model.parse_line('Курс "USD" "RUB" 75.5 2026.02.25')
        self.assertEqual(rate.currency_from, "USD")
        self.assertEqual(rate.rate, 75.5)

    def test_missing_quotes(self):
        with self.assertRaises(ParseError):
            self.model.parse_line('Курс USD "RUB" 75.5 2026.02.25')


class TestLoadFromFile(unittest.TestCase):
    def setUp(self): self.model = CurrencyModel()

    def test_load_valid_and_invalid_lines(self):
        content = '"USD" "RUB" 75.5 2026.02.25\nbad line\n"EUR" "RUB" 85.0 2026.03.01\n'
        path = write_tmp(content)
        try:
            self.model.load_from_file(path)
            self.assertEqual(len(self.model.records), 2)
            self.assertEqual(self.model.records[0].currency_from, "USD")
        finally:
            os.remove(path)

class TestAddDelete(unittest.TestCase):
    def setUp(self): self.model = CurrencyModel()

    def test_add_record_valid(self):
        self.model.add_record('"USD" "RUB" 75.5 2026.02.25')
        self.assertEqual(len(self.model.records), 1)

    def test_delete_single(self):
        self.model.records = [make_rate("USD"), make_rate("EUR")]
        self.model.delete_records([0])
        self.assertEqual(len(self.model.records), 1)
        self.assertEqual(self.model.records[0].currency_from, "EUR")


class TestPolymorphismAndCsv(unittest.TestCase):
    def setUp(self): self.model = CurrencyModel()

    def test_valid_csv(self):
        rate = self.model.parse_csv_line("USD,RUB,92.5,2026.02.15")
        self.assertEqual(rate.currency_from, "USD")
        
    def test_person_csv(self):
        person = self.model.parse_person_csv("Artem,RU,1000")
        self.assertIsInstance(person, Person)
        self.assertEqual(person.name, "Artem")
        
    def test_polymorphic_save(self):
        self.model.records = [
            make_rate("USD", "RUB", 92.5, date(2026, 2, 15)),
            Person("Artem", "RU", 1000.0)
        ]
        fd, path = tempfile.mkstemp(suffix=".txt")
        os.close(fd)
        try:
            self.model.save_to_file(path)
            with open(path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            self.assertTrue(lines[0].startswith('"USD"'))
            self.assertTrue(lines[1].startswith('Artem,RU'))
        finally:
            os.remove(path)


class TestRemoveByCondition(unittest.TestCase):
    def setUp(self):
        self.model = CurrencyModel()
        self.model.records = [
            CurrencyRate("USD", "RUB", 75.0, date(2026, 1, 10)),
            Person("Artem", "RU", 1000.0)
        ]

    def test_rem_rate(self):
        self.model.remove_by_condition("rate < 80")
        self.assertEqual(len(self.model.records), 1)
        self.assertIsInstance(self.model.records[0], Person) # Rate был удален

    def test_rem_person_money(self):
        self.model.remove_by_condition("money >= 500")
        self.assertEqual(len(self.model.records), 1)
        self.assertEqual(self.model.records[0].currency_from, "USD") # Person был удален

if __name__ == '__main__':
    unittest.main(verbosity=2)