import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sv_ttk  
from tkhtmlview import HTMLLabel
from model import CurrencyModel, ParseError # Подключаем нашу модель

class CurrencyApp(tk.Tk):
    def __init__(self, model: CurrencyModel):
        super().__init__()
        self.model = model  # Сохраняем ссылку на модель
        self.title("Управление курсами валют")
        self.geometry("700x550")
        self.resizable(False, False)
        self._create_widgets()
        self.update_table()

    def _create_widgets(self):
        # Верхний фрейм
        top_frame = ttk.Frame(self)
        top_frame.pack(pady=15, fill=tk.X, padx=15)

        ttk.Button(top_frame, text="Загрузить из файла", command=self.load_file).pack(side=tk.LEFT)
        ttk.Button(top_frame, text="Удалить выделенное", command=self.delete_selected).pack(side=tk.RIGHT)

        # Таблица
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

        # Фрейм для добавления
        add_frame = ttk.Frame(self)
        add_frame.pack(pady=5, fill=tk.X, padx=15)

        ttk.Label(add_frame, text="Новая запись:").pack(side=tk.LEFT, padx=(0, 10))
        self.entry_new = ttk.Entry(add_frame, width=40)
        self.entry_new.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entry_new.insert(0, 'Курс "USD" "RUB" 75.5 2026.02.25')
        ttk.Button(add_frame, text="Добавить", command=self.add_record).pack(side=tk.RIGHT)

        # Фрейм для HTML кнопки
        bottom_frame = ttk.Frame(self)
        bottom_frame.pack(pady=15, fill=tk.X, padx=15)
        ttk.Button(bottom_frame, text="Справка (HTML)", command=self.open_html_window).pack(side=tk.LEFT)

    def open_html_window(self):
        html_win = tk.Toplevel(self)
        html_win.title("Справка")
        html_win.geometry("750x650")
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
        </div>
        """
        html_label = HTMLLabel(html_win, html=my_html_content)
        html_label.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        ttk.Button(html_win, text="Закрыть", command=html_win.destroy).pack(pady=10)

    def update_table(self):
        for item in self.tree.get_children():
            self.tree.delete(item)
            
        for index, rate in enumerate(self.model.rates):
            self.tree.insert("", tk.END, iid=str(index), values=(
                rate.currency_from, rate.currency_to, rate.rate, rate.date
            ))

    def load_file(self):
        filepath = filedialog.askopenfilename(
            title="Выберите файл с данными",
            filetypes=[("Text files", "*.txt"), ("All files", "*.*")]
        )
        if not filepath:
            return
            
        try:
            added_count = self.model.load_from_file(filepath)
            self.update_table()
            messagebox.showinfo(
                "Результат", 
                f"Загружено записей: {added_count}.\nОшибочные строки пропущены (см. errors.log)"
            )
        except Exception as e:
            messagebox.showerror("Системная ошибка", f"Ошибка доступа к файлу:\n{e}")

    def add_record(self):
        text = self.entry_new.get().strip()
        if not text:
            messagebox.showwarning("Внимание", "Поле ввода пустое.")
            return
            
        try:
            self.model.add_record(text)
            self.update_table()
            self.entry_new.delete(0, tk.END)
        except ParseError as e:
            messagebox.showerror("Ошибка парсинга", f"{e}")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items:
            messagebox.showwarning("Внимание", "Выберите строку для удаления.")
            return
            
        indices = [int(item) for item in selected_items]
        self.model.delete_records(indices)
        self.update_table()

if __name__ == "__main__":
    # 1. Создаем Модель
    model = CurrencyModel()
    
    # 2. Передаем модель в View
    app = CurrencyApp(model)
    sv_ttk.set_theme("dark") 
    app.mainloop()