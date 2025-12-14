import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3
import pandas as pd
from datetime import datetime
import os

# ==============================================================================
# I. ЛОГІКА БАЗИ ДАНИХ (DBManager, SQLite)
# ==============================================================================

DATABASE_NAME = 'student_db.db'


def setup_database():
    """Створює таблицю 'Студенти' та додає початкові тестові дані."""

    # Видаляємо файл, щоб щоразу мати свіжий старт для демонстрації
    if os.path.exists(DATABASE_NAME):
        os.remove(DATABASE_NAME)

    CONN = sqlite3.connect(DATABASE_NAME)
    CURSOR = CONN.cursor()

    # Створення таблиці "Студенти"
    CURSOR.execute("""
                   CREATE TABLE IF NOT EXISTS Студенти
                   (
                       Код
                       INTEGER
                       PRIMARY
                       KEY,
                       ПІБ
                       TEXT
                       NOT
                       NULL,
                       Дата_Народження
                       TEXT,
                       Факультет
                       TEXT,
                       Група
                       TEXT
                   )
                   """)

    # Додавання тестових даних
    initial_students = [
        ('Іванов Іван', '2000-05-15', 'Комп. Інженерія', 'ІС-11'),
        ('Петрова Анна', '2001-11-20', 'Економіка', 'ЕК-22'),
        ('Сидоренко О.М.', '1999-03-01', 'Програмування', 'ПЗ-31')
    ]

    try:
        # Використовуємо NULL для автоінкременту Коду
        CURSOR.executemany("INSERT INTO Студенти VALUES (NULL, ?, ?, ?, ?)", initial_students)
        CONN.commit()
    except sqlite3.IntegrityError:
        pass

    CONN.close()


# Запуск налаштування бази даних перед запуском програми
setup_database()


class DBManager:
    """Керує підключенням до БД та забезпечує функції CRUD для GUI."""

    def __init__(self, db_name='student_db.db'):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.table_name = 'Студенти'
        self.columns = ['Код', 'ПІБ', 'Дата_Народження', 'Факультет', 'Група']

    def fetch_all(self):
        """Завантажує всі дані з таблиці."""
        query = f"SELECT * FROM {self.table_name} ORDER BY Код"
        return self.cursor.execute(query).fetchall()

    def insert_record(self, data):
        """Додає новий запис (імітація Insert + Post)."""
        # Data: (ПІБ, Дата_Народження, Факультет, Група)
        query = f"INSERT INTO {self.table_name} (ПІБ, Дата_Народження, Факультет, Група) VALUES (?, ?, ?, ?)"
        self.cursor.execute(query, data)
        self.conn.commit()

    def update_record(self, record_id, data):
        """Оновлює існуючий запис (імітація Edit + Post)."""
        # Data: (ПІБ, Дата_Народження, Факультет, Група, Код)
        query = f"UPDATE {self.table_name} SET ПІБ=?, Дата_Народження=?, Факультет=?, Група=? WHERE Код=?"
        self.cursor.execute(query, data + (record_id,))
        self.conn.commit()

    def delete_record(self, record_id):
        """Видаляє запис (імітація Delete)."""
        query = f"DELETE FROM {self.table_name} WHERE Код=?"
        self.cursor.execute(query, (record_id,))
        self.conn.commit()

    def close(self):
        self.conn.close()


# ==============================================================================
# II. ГРАФІЧНИЙ ІНТЕРФЕЙС (GUI)
# ==============================================================================

class StudentDBApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Управління базою даних «Студенти групи» (Python/SQLite)")
        self.geometry("900x550")

        # Ініціалізація менеджера БД
        self.db_manager = DBManager()

        # Налаштування стилю для таблиці (Treeview)
        style = ttk.Style()
        style.theme_use("clam")  # Тема, яка добре виглядає на macOS

        self.create_widgets()
        self.load_data()

    def create_widgets(self):
        # Фрейм для таблиці
        tree_frame = ttk.Frame(self)
        tree_frame.pack(pady=10, padx=10, fill="both", expand=True)

        # Створення таблиці (Treeview)
        self.tree = ttk.Treeview(tree_frame, columns=self.db_manager.columns, show="headings")

        # Налаштування заголовків стовпців
        column_widths = [50, 200, 100, 150, 80]
        column_names = {
            'Код': 'Код',
            'ПІБ': 'ПІБ',
            'Дата_Народження': 'Дата народження',
            'Факультет': 'Факультет',
            'Група': 'Група'
        }

        for col, width in zip(self.db_manager.columns, column_widths):
            self.tree.heading(col, text=column_names[col])
            self.tree.column(col, width=width, anchor=tk.CENTER)

        self.tree.pack(side="left", fill="both", expand=True)

        # Додавання скролбару
        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side="right", fill="y")
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Фрейм для кнопок (управління даними)
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10, padx=10)

        # Кнопки CRUD-операцій (взаємодія)
        ttk.Button(button_frame, text="Додати Студента", command=self.open_add_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Редагувати", command=self.open_edit_window).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Видалити", command=self.delete_record).pack(side=tk.LEFT, padx=5)

        # Кнопка для реалізації сортування (як приклад)
        ttk.Button(button_frame, text="Сортувати за ПІБ", command=lambda: self.sort_column('ПІБ', False)).pack(
            side=tk.LEFT, padx=20)

        # Прив'язка події (подвійний клік для редагування)
        self.tree.bind("<Double-1>", self.on_double_click)

    # --- Методи Керування Даними ---

    def load_data(self):
        """Очищає Treeview та завантажує актуальні дані з БД."""
        # Очистити існуючі дані
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Завантажити нові дані
        records = self.db_manager.fetch_all()
        for record in records:
            # Вставляємо дані в Treeview
            self.tree.insert("", tk.END, values=record)

    def open_add_window(self):
        """Відкриває вікно для додавання нового запису."""
        # Створюємо модальне вікно, яке імітує форму в C++ Builder
        AddWindow(self)

    def open_edit_window(self):
        """Відкриває вікно для редагування обраного запису."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Редагування", "Будь ласка, виберіть запис для редагування.")
            return

        # Отримати значення обраного рядка
        values = self.tree.item(selected_item, 'values')
        # values[0] - це Код студента (первинний ключ)
        EditWindow(self, values)

    def on_double_click(self, event):
        """Обробник подвійного кліку для швидкого редагування."""
        self.open_edit_window()

    def delete_record(self):
        """Викликає метод видалення з БД."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Видалення", "Будь ласка, виберіть запис для видалення.")
            return

        # Отримати Код студента (перший елемент у values)
        record_values = self.tree.item(selected_item, 'values')
        record_id = record_values[0]
        record_name = record_values[1]

        # Імітація MessageBox (як у C++ коді)
        if messagebox.askyesno("Увага!!!", f"Ви дійсно хочете видалити студента {record_name}?"):
            try:
                self.db_manager.delete_record(record_id)
                messagebox.showinfo("Успіх", "Запис видалено.")
                self.load_data()  # Оновлення таблиці
            except Exception as e:
                messagebox.showerror("Помилка БД", f"Не вдалося видалити запис: {e}")

    def sort_column(self, col, reverse):
        """Сортує дані в Treeview."""
        # Функція сортування для Treeview (реалізує Завдання 6)

        # Отримуємо всі дані
        data = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]

        # Сортуємо
        data.sort(reverse=reverse)

        # Переставляємо відсортовані рядки
        for index, (val, k) in enumerate(data):
            self.tree.move(k, '', index)

        # Налаштовуємо наступний клік для зміни порядку
        self.tree.heading(col, command=lambda: self.sort_column(col, not reverse))


# ==============================================================================
# III. МОДАЛЬНІ ВІКНА (ФОРМИ ДЛЯ ВВЕДЕННЯ ДАНИХ)
# ==============================================================================

class DataWindow(tk.Toplevel):
    """Базовий клас для вікон додавання та редагування."""

    def __init__(self, master, title):
        super().__init__(master)
        self.transient(master)  # Зробити модальним
        self.title(title)
        self.master = master

        self.labels = ['ПІБ:', 'Дата народження (РРРР-ММ-ДД):', 'Факультет:', 'Група:']
        self.entries = {}

        self.create_input_widgets()
        self.grab_set()  # Фокусуватись на цьому вікні
        self.protocol("WM_DELETE_WINDOW", self.destroy)
        self.focus_force()

    def create_input_widgets(self):
        form_frame = ttk.Frame(self, padding="10")
        form_frame.pack(fill="both", expand=True)

        # Створення міток та полів введення
        for i, text in enumerate(self.labels):
            ttk.Label(form_frame, text=text).grid(row=i, column=0, sticky="w", pady=5, padx=5)
            entry = ttk.Entry(form_frame, width=40)
            entry.grid(row=i, column=1, pady=5, padx=5, sticky="ew")
            self.entries[self.labels[i]] = entry

        # Кнопки
        button_frame = ttk.Frame(self)
        button_frame.pack(pady=10)

        ttk.Button(button_frame, text="Скасувати", command=self.destroy).pack(side=tk.LEFT, padx=5)

    def get_data(self):
        """Збирає дані з полів введення."""
        # Порядок: ПІБ, Дата_Народження, Факультет, Група
        return (
            self.entries[self.labels[0]].get(),
            self.entries[self.labels[1]].get(),
            self.entries[self.labels[2]].get(),
            self.entries[self.labels[3]].get(),
        )


class AddWindow(DataWindow):
    """Вікно для додавання нового запису."""

    def __init__(self, master):
        super().__init__(master, "Додати нового студента")

        # Додаємо кнопку "Зберегти" (Post)
        ttk.Button(self.children['!frame2'], text="Зберегти", command=self.save_record).pack(side=tk.LEFT, padx=5)

    def save_record(self):
        """Зберігає новий запис до БД."""
        data = self.get_data()

        if not all(data):
            messagebox.showwarning("Помилка", "Будь ласка, заповніть всі поля.")
            return

        try:
            self.master.db_manager.insert_record(data)
            messagebox.showinfo("Успіх", "Запис успішно додано.")
            self.master.load_data()  # Оновлення таблиці
            self.destroy()
        except Exception as e:
            messagebox.showerror("Помилка БД", f"Помилка при додаванні запису: {e}")


class EditWindow(DataWindow):
    """Вікно для редагування існуючого запису."""

    def __init__(self, master, record_values):
        super().__init__(master, "Редагувати запис")
        self.record_id = record_values[0]  # Код (PK)

        # Заповнюємо поля поточною інформацією
        self.fill_entries(record_values[1:])

        # Додаємо кнопку "Зберегти" (Post)
        ttk.Button(self.children['!frame2'], text="Зберегти Зміни", command=self.update_record).pack(side=tk.LEFT,
                                                                                                     padx=5)

    def fill_entries(self, values):
        """Заповнює поля введення даними з обраного запису."""
        # values[0] - ПІБ, values[1] - Дата_Народження, ...
        for i, label in enumerate(self.labels):
            self.entries[label].insert(0, values[i])

    def update_record(self):
        """Зберігає оновлений запис до БД (імітація Post)."""
        data = self.get_data()

        if not all(data):
            messagebox.showwarning("Помилка", "Будь ласка, заповніть всі поля.")
            return

        try:
            self.master.db_manager.update_record(self.record_id, data)
            messagebox.showinfo("Успіх", "Запис успішно оновлено.")
            self.master.load_data()  # Оновлення таблиці
            self.destroy()
        except Exception as e:
            messagebox.showerror("Помилка БД", f"Помилка при оновленні запису: {e}")


# ==============================================================================
# IV. ЗАПУСК ПРОГРАМИ
# ==============================================================================

if __name__ == "__main__":
    app = StudentDBApp()


    # Викликаємо метод close для коректного закриття з'єднання з БД при виході
    def on_closing():
        try:
            app.db_manager.close()
        finally:
            app.destroy()


    app.protocol("WM_DELETE_WINDOW", on_closing)
    app.mainloop()