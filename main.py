import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import sv_ttk  
from tkhtmlview import HTMLLabel
from model import CurrencyModel, ParseError 

# Перехватчик логов для вывода в поле GUI
class GuiLogHandler(logging.Handler):
    def __init__(self, text_widget):
        super().__init__()
        self.text_widget = text_widget
    def emit(self, record):
        msg = self.format(record)
        def append():
            self.text_widget.config(state=tk.NORMAL)
            self.text_widget.insert(tk.END, msg + "\n")
            self.text_widget.config(state=tk.DISABLED)
            self.text_widget.see(tk.END)
        self.text_widget.after(0, append)

class CurrencyApp(tk.Tk):
    def __init__(self, model: CurrencyModel):
        super().__init__()
        self.model = model  
        self.title("Управление курсами валют")
        self.geometry("1200x400") 
        self.resizable(False, False) 
        self._create_widgets()
        self._setup_logging()
        self.update_table()

    def _create_widgets(self):
        # ГЛАВНЫЙ КОНТЕЙНЕР ДЛЯ ВСЕГО
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        
        self.left_side = ttk.Frame(self.main_container)
        self.left_side.pack(side=tk.LEFT, padx=15, fill=tk.Y)

        
        
        top_frame = ttk.Frame(self.left_side)
        top_frame.pack(pady=15, fill=tk.X)
        top_frame.columnconfigure(0, weight=1)
        top_frame.columnconfigure(1, weight=1)
        top_frame.columnconfigure(2, weight=1)

        ttk.Button(top_frame, text="Загрузить из файла", command=self.load_file).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(top_frame, text="Справка (HTML)", command=self.open_html_window).grid(row=0, column=1)
        ttk.Button(top_frame, text="Удалить выделенное", command=self.delete_selected).grid(row=0, column=2, sticky=tk.E)

        columns = ("from", "to", "rate", "date")
        self.tree = ttk.Treeview(self.left_side, columns=columns, show="headings", height=10)
        self.tree.heading("from", text="Из валюты"); self.tree.heading("to", text="В валюту")
        self.tree.heading("rate", text="Курс"); self.tree.heading("date", text="Дата")
        self.tree.column("from", width=100, anchor=tk.CENTER)
        self.tree.column("to", width=100, anchor=tk.CENTER)
        self.tree.column("rate", width=150, anchor=tk.CENTER)
        self.tree.column("date", width=150, anchor=tk.CENTER)
        self.tree.pack(pady=5)

        add_frame = ttk.Frame(self.left_side)
        add_frame.pack(pady=5, fill=tk.X)
        ttk.Label(add_frame, text="Новая запись:").pack(side=tk.LEFT, padx=(0, 10))
        self.entry_new = ttk.Entry(add_frame, width=40)
        self.entry_new.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entry_new.insert(0, 'Курс "USD" "RUB" 75.5 2026.02.25')
        ttk.Button(add_frame, text="Добавить", command=self.add_record).pack(side=tk.RIGHT)

    
        self.right_side = ttk.LabelFrame(self.main_container, text=" Лог ошибок (errors.log) ")
        self.right_side.pack(side=tk.RIGHT, padx=15, pady=(15,40), fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.right_side, state=tk.DISABLED, width=50,
                                bg="#1e1e1e", fg="#ff6b6b", font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        scrollbar = ttk.Scrollbar(self.right_side, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _setup_logging(self):
        handler = GuiLogHandler(self.log_text)
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logging.getLogger().addHandler(handler)

    # Твоя оригинальная справка 
    def open_html_window(self):
        html_win = tk.Toplevel(self)
        html_win.title("Справка")
        html_win.geometry("900x800")
        html_win.transient(self)
        html_win.grab_set()
        image_url = "https://kartinka.top/files/collections/107/p720.jpg"
        my_html_content = f"""
        <div style="text-align: center;">
            <a href="{image_url}"><img src="{image_url}" title="{image_url}" width="100%" height="100%"></a><br>
            <h1 style="color: #000000; text-align: center;">Справка</h1>
            <p>Эта программа предназначена для <b>управления курсами валют</b>.</p>
        </div>"""
        html_label = HTMLLabel(html_win, html=my_html_content)
        html_label.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        ttk.Button(html_win, text="Закрыть", command=html_win.destroy).pack(pady=10)

    def update_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for index, rate in enumerate(self.model.rates):
            self.tree.insert("", tk.END, iid=str(index), values=(rate.currency_from, rate.currency_to, rate.rate, rate.date))

    def load_file(self):
        filepath = filedialog.askopenfilename(title="Выберите файл с данными", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not filepath: return
        try:
            added_count = self.model.load_from_file(filepath)
            self.update_table()
            messagebox.showinfo("Результат", f"Загружено записей: {added_count}.\nОшибочные строки пропущены (см. errors.log)")
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
    model = CurrencyModel()
    app = CurrencyApp(model)
    sv_ttk.set_theme("dark") 
    app.mainloop()