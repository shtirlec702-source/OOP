import re
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from datetime import datetime
import sv_ttk  
from tkhtmlview import HTMLLabel  #  HTML

class CurrencyRate:
    def __init__(self, currency_from: str, currency_to: str, rate: float, rate_date: datetime.date):
        self.currency_from = currency_from
        self.currency_to = currency_to
        self.rate = rate
        self.date = rate_date

    def __str__(self) -> str:
        return f"Курс: {self.currency_from} = {self.rate} {self.currency_to} (Дата: {self.date})"


def extract_currencies(line: str) -> tuple[str, str, str]:
    currencies = re.findall(r'"([^"]+)"', line)
    if len(currencies) < 2:
        raise ValueError('Нужно указать две валюты в кавычках, например: "USD" "RUB"')
    remaining_line = re.sub(r'"[^"]+"', '', line)
    return currencies[0], currencies[1], remaining_line

def extract_date(parts: list[str]) -> datetime.date:
    for part in parts:
        if part.count('.') == 2:
            try:
                return datetime.strptime(part, "%Y.%m.%d").date()
            except ValueError:
                continue
    raise ValueError("Не найдена дата в формате гггг.мм.дд")

def extract_rate(parts: list[str]) -> float:
    for part in parts:
        if part.count('.') != 2:
            try:
                return float(part)
            except ValueError:
                continue
    raise ValueError("Не найден числовой курс")

def parse_currency_string(line: str) -> CurrencyRate:
    curr_from, curr_to, remaining_text = extract_currencies(line)
    parts = remaining_text.split()
    rate_val = extract_rate(parts)
    date_val = extract_date(parts)
    return CurrencyRate(curr_from, curr_to, rate_val, date_val)

def load_rates_from_file(filepath: str) -> list[CurrencyRate]:
    rates = []
    with open(filepath, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line:
                rates.append(parse_currency_string(line))
    return rates


class CurrencyApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управление курсами валют")
        self.geometry("700x500")
        self.resizable(False, False)
        self.rates: list[CurrencyRate] = []
        self._create_widgets()

    def _create_widgets(self):
        
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=15, fill=tk.X, padx=15)

        
        btn_load = ttk.Button(top_frame, text="Загрузить из файла", command=self.load_file)
        btn_load.pack(side=tk.LEFT)

        btn_delete = ttk.Button(top_frame, text="Удалить выделенное", command=self.delete_selected)
        btn_delete.pack(side=tk.RIGHT)

        
        columns = ("from", "to", "rate", "date")
        self.tree = ttk.Treeview(self, columns=columns, show="headings", height=10)
        self.tree.heading("from", text="Из валюты")
        self.tree.heading("to", text="В валюту")
        self.tree.heading("rate", text="Курс")
        self.tree.heading("date", text="Дата")
        
        self.tree.column("from", width=100, anchor=tk.CENTER)
        self.tree.column("to", width=100, anchor=tk.CENTER)
        self.tree.column("rate", width=150, anchor=tk.CENTER)
        self.tree.column("date", width=150, anchor=tk.CENTER)
        
        self.tree.pack(expand=True, fill=tk.BOTH, padx=15, pady=5)


           # Нижний блок с добавлением и кнопкой HTML
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(pady=15, fill=tk.X, padx=15)

        # --- НАША НОВАЯ КНОПКА ДЛЯ HTML-ОКНА ---
        btn_html = ttk.Button(bottom_frame, text="Справка (HTML)", command=self.open_html_window)
        btn_html.pack(side=tk.LEFT, padx=(0, 15))
        # ---------------------------------------

        
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(pady=15, fill=tk.X, padx=15)

        
        ttk.Label(bottom_frame, text="Новая запись:").pack(side=tk.LEFT, padx=(0, 10))
        
        self.entry_new = ttk.Entry(bottom_frame, width=40)
        self.entry_new.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entry_new.insert(0, 'Курс "USD" "RUB" 75.5 2026.02.25')
        
        btn_add = ttk.Button(bottom_frame, text="Добавить", command=self.add_record)
        btn_add.pack(side=tk.RIGHT)

    # --- ФУНКЦИЯ СОЗДАНИЯ НОВОГО ОКНА ---
    def open_html_window(self):
        # Создаем дочернее окно (Toplevel) поверх основного
        html_win = tk.Toplevel(self)
        html_win.title("Справка")
        html_win.geometry("750x650")
        # Делаем так, чтобы окно не теряло фокус 
        html_win.transient(self)
        html_win.grab_set()

        image_url = "https://kartinka.top/files/collections/107/p720.jpg"
       
        my_html_content = f"""
        <div style="text-align: center;">
            <a href="{image_url}">
                <img src="{image_url}" title="{image_url}" width="100%" height="400">
            </a>
            <br>
        <h1 style="color: #000000; text-align: center;">Справка</h1>
        <p>Эта программа предназначена для <b>управления курсами валют</b>.</p>
          <div style="text-align: center;">
            <img src="b6fc0514cabfa0f434278903084c594c-3419148314.jpg" > </div>
        """


        
        html_label = HTMLLabel(html_win, html=my_html_content)
        html_label.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)

       
        btn_close = ttk.Button(html_win, text="Закрыть", command=html_win.destroy)
        btn_close.pack(pady=10)
    # ------------------------------------


    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for index, rate in enumerate(self.rates):
            self.tree.insert("", tk.END, iid=str(index), values=(
                rate.currency_from, 
                rate.currency_to, 
                rate.rate, 
                rate.date
            ))

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
            
        try:
            loaded_rates = load_rates_from_file(filepath)
            self.rates.extend(loaded_rates)
            self.update_table()
            messagebox.showinfo("Успех", f"Успешно загружено {len(loaded_rates)} записей.")
        except Exception as e:
            messagebox.showerror("Ошибка", f"Ошибка при чтении файла:\n{e}")

    def add_record(self):
        text = self.entry_new.get().strip()
        if not text:
            messagebox.showwarning("Внимание", "Поле ввода пустое.")
            return
            
        try:
            new_rate = parse_currency_string(text)
            self.rates.append(new_rate)
            self.update_table()
            self.entry_new.delete(0, tk.END)
        except Exception as e:
            messagebox.showerror("Ошибка парсинга", f"Проверьте формат строки.\n{e}")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите строку для удаления.")
            return
            
        indices_to_delete = sorted([int(item) for item in selected_items], reverse=True)
        for index in indices_to_delete:
            self.rates.pop(index)
            
        self.update_table()


if __name__ == "__main__":
    app = CurrencyApp()
    
    
    sv_ttk.set_theme("dark") 
    
    app.mainloop()