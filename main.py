import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import logging
import sv_ttk
from tkhtmlview import HTMLLabel
from model import CurrencyModel, ParseError

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
        self.title("Управление данными (Полиморфизм)")
        self.geometry("1200x500")
        self.resizable(False, False)
        self._create_widgets()
        self._setup_logging()
        self.update_table()

    def _create_widgets(self):
        self.main_container = ttk.Frame(self)
        self.main_container.pack(fill=tk.BOTH, expand=True)

        self.left_side = ttk.Frame(self.main_container)
        self.left_side.pack(side=tk.LEFT, padx=15, fill=tk.Y)

        top_frame = ttk.Frame(self.left_side)
        top_frame.pack(pady=15, fill=tk.X)
        for i in range(4): top_frame.columnconfigure(i, weight=1)

        ttk.Button(top_frame, text="Загрузить из файла", command=self.load_file).grid(row=0, column=0, sticky=tk.W)
        ttk.Button(top_frame, text="Справка (HTML)", command=self.open_html_window).grid(row=0, column=1)
        ttk.Button(top_frame, text="Удалить выделенное", command=self.delete_selected).grid(row=0, column=2)
        ttk.Button(top_frame, text="Выполнить команды", command=self.load_commands_file).grid(row=0, column=3, sticky=tk.E)

        # ── ЕДИНАЯ ТАБЛИЦА (Полиморфизм) ─────────────────────────────────
        ttk.Label(self.left_side, text="Все записи (Курсы и Персоны):", font=("", 9, "bold")).pack(anchor=tk.W, pady=(0, 2))
        columns = ("type", "col1", "col2", "col3", "col4")
        self.tree = ttk.Treeview(self.left_side, columns=columns, show="headings", height=12)
        self.tree.heading("type", text="Тип записи")
        self.tree.heading("col1", text="Из валюты / Имя")
        self.tree.heading("col2", text="В валюту / Страна")
        self.tree.heading("col3", text="Курс / Сумма")
        self.tree.heading("col4", text="Дата / —")
        self.tree.column("type", width=100, anchor=tk.CENTER)
        self.tree.column("col1", width=120, anchor=tk.CENTER)
        self.tree.column("col2", width=120, anchor=tk.CENTER)
        self.tree.column("col3", width=100, anchor=tk.CENTER)
        self.tree.column("col4", width=100, anchor=tk.CENTER)
        self.tree.pack(pady=(0, 5))

        add_frame = ttk.Frame(self.left_side)
        add_frame.pack(pady=3, fill=tk.X)
        ttk.Label(add_frame, text="Новый курс:").pack(side=tk.LEFT, padx=(0, 10))
        self.entry_new = ttk.Entry(add_frame, width=40)
        self.entry_new.pack(side=tk.LEFT, expand=True, fill=tk.X, padx=(0, 10))
        self.entry_new.insert(0, 'Курс "USD" "RUB" 75.5 2026.02.25')
        ttk.Button(add_frame, text="Добавить", command=self.add_record).pack(side=tk.RIGHT)

        hint = ('ADD USD,RUB,92.5,2026.02.15  |  ADD Artem,RU,1000  |  '
                'REM rate<80  |  REM money<100  |  REM country==RU  |  SAVE out.txt')
        ttk.Label(self.left_side, text=hint, foreground='gray', font=('Consolas', 8)).pack(anchor=tk.W, pady=(5, 5))

        self.right_side = ttk.LabelFrame(self.main_container, text=" Лог ошибок (errors.log) ")
        self.right_side.pack(side=tk.RIGHT, padx=15, pady=(15, 20), fill=tk.BOTH, expand=True)

        self.log_text = tk.Text(self.right_side, state=tk.DISABLED, width=45,
                                bg="#1e1e1e", fg="#ff6b6b", font=("Consolas", 9))
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5, pady=5)
        scrollbar = ttk.Scrollbar(self.right_side, command=self.log_text.yview)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.log_text.config(yscrollcommand=scrollbar.set)

    def _setup_logging(self):
        handler = GuiLogHandler(self.log_text)
        handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))
        logging.getLogger().addHandler(handler)

    def open_html_window(self):
        html_win = tk.Toplevel(self)
        html_win.title("Справка"); html_win.geometry("900x800")
        html_win.transient(self); html_win.grab_set()
        image_url = "https://kartinka.top/files/collections/107/p720.jpg"
        my_html_content = f"""
        <div style="text-align: center;">
            <a href="{image_url}"><img src="{image_url}" title="{image_url}" width="100%" height="100%"></a><br>
            <h1 style="color: #000000; text-align: center;">Справка</h1>
            <p>Эта программа предназначена для управления курсами валют и персонами в <b>единой таблице</b>.</p>
        </div>"""
        html_label = HTMLLabel(html_win, html=my_html_content)
        html_label.pack(expand=True, fill=tk.BOTH, padx=15, pady=10)
        ttk.Button(html_win, text="Закрыть", command=html_win.destroy).pack(pady=10)

    def update_table(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        for index, record in enumerate(self.model.records):
            # ПОЛИМОРФНЫЙ ВЫЗОВ to_row() — таблице неважно курс это или человек
            self.tree.insert("", tk.END, iid=str(index), values=record.to_row())

    def load_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if not filepath: return
        try:
            self.model.load_from_file(filepath)
            self.update_table()
        except Exception as e:
            messagebox.showerror("Ошибка", f"{e}")

    def add_record(self):
        text = self.entry_new.get().strip()
        if not text: return
        try:
            self.model.add_record(text)
            self.update_table()
            self.entry_new.delete(0, tk.END)
        except ParseError as e:
            messagebox.showerror("Ошибка парсинга", f"{e}")

    def delete_selected(self):
        selected_items = self.tree.selection()
        if not selected_items: return
        indices = [int(item) for item in selected_items]
        self.model.delete_records(indices)
        self.update_table()

    def load_commands_file(self):
        filepath = filedialog.askopenfilename(filetypes=[("All files", "*.*")])
        if not filepath: return
        try:
            stats = self.model.execute_commands_from_file(filepath)
            self.update_table()
            messagebox.showinfo("Команды выполнены", 
                f"Добавлено: {stats['add']}, Удалено: {stats['rem']}, Ошибок: {stats['errors']}")
        except OSError as e:
            messagebox.showerror("Ошибка", f"{e}")

if __name__ == "__main__":
    model = CurrencyModel()
    app = CurrencyApp(model)
    sv_ttk.set_theme("dark")
    app.mainloop()