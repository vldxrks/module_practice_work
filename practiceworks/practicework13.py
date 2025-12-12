import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import sqlite3
from PIL import Image, ImageTk
import io
import os

# --- КОНСТАНТИ БД ---
DB_NAME = 'students.db'
TABLE_NAME = 'Студенти'
PHOTO_FIELD = 'Фотографія'
FIELDS = [
    ("ПІБ", "Короткий текст"),
    ("Дата_народження", "Дата і час"),
    ("Факультет", "Короткий текст"),
    ("Група", "Короткий текст"),
]


class StudentDBApp:
    def __init__(self, master):
        self.master = master
        master.title("Управління базою даних «Студенти групи» (Python/SQLite)")

        self.current_student_id = None
        self.current_photo_data = None  # Зберігає бінарні дані поточної фотографії

        self.setup_db()
        self.create_widgets()
        self.load_data()

    def setup_db(self):
        """Створює базу даних та таблицю, якщо вони не існують."""
        self.conn = sqlite3.connect(DB_NAME)
        self.cursor = self.conn.cursor()

        # SQL-запит для створення таблиці
        fields_sql = ",\n".join([f"{name} TEXT" for name, _ in FIELDS])

        sql_create_table = f"""
        CREATE TABLE IF NOT EXISTS {TABLE_NAME} (
            ID INTEGER PRIMARY KEY AUTOINCREMENT,
            {fields_sql},
            {PHOTO_FIELD} BLOB
        )
        """
        self.cursor.execute(sql_create_table)
        self.conn.commit()

        # Додавання тестового запису, якщо таблиця порожня
        self.cursor.execute(f"SELECT COUNT(*) FROM {TABLE_NAME}")
        if self.cursor.fetchone()[0] == 0:
            self.cursor.execute(f"""
             INSERT INTO {TABLE_NAME} (ПІБ, Група, Факультет) 
             VALUES ('Тестовий Студент', 'ІС-11', 'Комп. Інженерія')
             """)
            self.conn.commit()

    def create_widgets(self):
        """Створення компонентів інтерфейсу."""

        main_frame = ttk.Frame(self.master, padding="10")
        main_frame.pack(fill='both', expand=True)

        # Фрейм для таблиці та фотографії (верхня частина вікна)
        content_frame = ttk.Frame(main_frame)
        content_frame.pack(fill='both', expand=True)

        # 1. DBGrid Еквівалент (ttk.Treeview)
        # -----------------------------------------------------------------
        tree_frame = ttk.Frame(content_frame)
        tree_frame.pack(side='left', fill='both', expand=True, pady=10, padx=(0, 10))

        columns = ("ID",) + tuple(name for name, _ in FIELDS)
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings')

        self.tree.heading("ID", text="Код", anchor='w')
        self.tree.column("ID", width=50, stretch=False)

        for name in (name for name, _ in FIELDS):
            self.tree.heading(name, text=name.replace('_', ' '), anchor='w')
            self.tree.column(name, width=120, stretch=True)

        self.tree.bind('<<TreeviewSelect>>', self.on_record_select)
        self.tree.pack(side='left', fill='both', expand=True)

        scrollbar = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        scrollbar.pack(side='right', fill='y')
        self.tree.configure(yscrollcommand=scrollbar.set)

        # 2. Image Еквівалент (tk.Label)
        # -----------------------------------------------------------------
        image_frame = ttk.LabelFrame(content_frame, text="Фотографія", padding="5")
        image_frame.pack(fill='y', side='right')

        self.photo_label = tk.Label(image_frame, width=200, height=200, relief="solid", text="Немає фотографії",
                                    fg='grey')
        self.photo_label.pack(padx=5, pady=5)

        # 3. Кнопки (аналог Завантажити/Зберегти)
        # -----------------------------------------------------------------
        btn_load = ttk.Button(image_frame, text="Завантажити фото", command=self.load_photo_to_form)
        btn_load.pack(fill='x', pady=5)

        btn_save = ttk.Button(image_frame, text="Зберегти фото", command=self.save_photo_to_db)
        btn_save.pack(fill='x', pady=5)

        # 4. DBNavigator Еквівалент (Кнопки додавання, видалення, оновлення)
        # -----------------------------------------------------------------
        nav_frame = ttk.Frame(main_frame)
        nav_frame.pack(fill='x', pady=10)  # Розміщуємо його внизу основного фрейму

        # Створюємо кнопки, використовуючи менеджер Grid для чіткого позиціонування

        # Кнопка Додати запис
        btn_add = ttk.Button(nav_frame, text="Додати запис", command=self.add_record)
        btn_add.grid(row=0, column=0, padx=5, pady=5)

        # Кнопка Видалити запис
        btn_delete = ttk.Button(nav_frame, text="Видалити запис", command=self.delete_record)
        btn_delete.grid(row=0, column=1, padx=5, pady=5)

        # Створюємо пустий стовпець, щоб кнопки залишалися зліва
        nav_frame.grid_columnconfigure(2, weight=1)

    # --- МЕТОДИ РОБОТИ З ДАНИМИ ---

    def load_data(self):
        """Завантажує дані з БД та відображає їх у Treeview (DBGrid)."""

        for row in self.tree.get_children():
            self.tree.delete(row)

        sql = f"SELECT ID, {', '.join(name for name, _ in FIELDS)} FROM {TABLE_NAME}"
        self.cursor.execute(sql)

        for row in self.cursor.fetchall():
            self.tree.insert('', 'end', values=row)

    def on_record_select(self, event):
        """
        Еквівалент OnCellClick DBGrid.
        Витягує BLOB-дані та відображає зображення.
        """
        selected_item = self.tree.focus()
        if not selected_item:
            return

        values = self.tree.item(selected_item, 'values')
        self.current_student_id = values[0]

        # 1. Запит до БД для отримання фотографії
        sql = f"SELECT {PHOTO_FIELD} FROM {TABLE_NAME} WHERE ID = ?"
        self.cursor.execute(sql, (self.current_student_id,))
        self.current_photo_data = self.cursor.fetchone()[0]

        # 2. Відображення зображення
        self.display_photo()

    def display_photo(self):
        """Відображає self.current_photo_data у віджеті photo_label."""

        # Очищення попереднього зображення
        self.photo_label.config(image='', text="Немає фотографії", fg='grey')

        if self.current_photo_data:
            try:
                # Перетворення BLOB (байт) на об'єкт PIL Image
                image = Image.open(io.BytesIO(self.current_photo_data))

                # Масштабування для відображення
                ratio = min(200 / image.width, 200 / image.height)
                new_size = (int(image.width * ratio), int(image.height * ratio))
                image = image.resize(new_size, Image.Resampling.LANCZOS)

                self.photo_tk = ImageTk.PhotoImage(image)
                self.photo_label.config(image=self.photo_tk, text="")
                self.photo_label.image = self.photo_tk
            except Exception as e:
                self.photo_label.config(image='', text="Помилка завантаження фото", fg='red')
                print(f"Помилка відображення зображення: {e}")
        else:
            self.photo_label.config(text="Немає фотографії", fg='grey')

    # --- МЕТОДИ КНОПОК ---

    def load_photo_to_form(self):
        """Код кнопки "Завантажити фото" (завантажує фото у пам'ять додатка)."""
        if self.current_student_id is None:
            messagebox.showwarning("Помилка", "Будь ласка, виберіть запис для оновлення.")
            return

        file_path = filedialog.askopenfilename(
            title="Виберіть фотографію",
            filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.gif")]
        )

        if file_path:
            try:
                # Читання файлу як бінарних даних
                with open(file_path, 'rb') as file:
                    self.current_photo_data = file.read()

                # Відображення нового фото
                self.display_photo()
                messagebox.showinfo("Увага", "Фото завантажено у форму. Натисніть 'Зберегти фото' для оновлення БД.")

            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося завантажити файл: {e}")

    def save_photo_to_db(self):
        """Код кнопки "Зберегти фото" (зберігає дані self.current_photo_data у БД як BLOB)."""
        if self.current_student_id is None or self.current_photo_data is None:
            messagebox.showwarning("Помилка", "Спочатку виберіть запис та завантажте фото.")
            return

        try:
            blob_data = sqlite3.Binary(self.current_photo_data)

            sql = f"UPDATE {TABLE_NAME} SET {PHOTO_FIELD} = ? WHERE ID = ?"
            self.cursor.execute(sql, (blob_data, self.current_student_id))
            self.conn.commit()

            messagebox.showinfo("Успіх", f"Фотографію для ID {self.current_student_id} успішно збережено!")

        except Exception as e:
            messagebox.showerror("Помилка БД", f"Не вдалося зберегти фото у базу даних: {e}")

    def add_record(self):
        """Додає новий порожній запис (еквівалент DBNavigator '+')."""
        try:
            sql = f"INSERT INTO {TABLE_NAME} (ПІБ, Група) VALUES (?, ?)"
            self.cursor.execute(sql, ("Новий студент", "Невідома"))
            self.conn.commit()
            self.load_data()
            messagebox.showinfo("Успіх", "Новий запис додано. Клацніть на нього, щоб додати фото.")
        except Exception as e:
            messagebox.showerror("Помилка", f"Не вдалося додати запис: {e}")

    def delete_record(self):
        """Видаляє вибраний запис (еквівалент DBNavigator 'х')."""
        selected_item = self.tree.focus()
        if not selected_item:
            messagebox.showwarning("Помилка", "Будь ласка, виберіть запис для видалення.")
            return

        values = self.tree.item(selected_item, 'values')
        student_id = values[0]

        if messagebox.askyesno("Підтвердження", f"Ви впевнені, що хочете видалити запис ID: {student_id}?"):
            try:
                sql = f"DELETE FROM {TABLE_NAME} WHERE ID = ?"
                self.cursor.execute(sql, (student_id,))
                self.conn.commit()
                self.load_data()
                self.photo_label.config(image='', text="Немає фотографії")
                self.current_student_id = None
                self.current_photo_data = None
                messagebox.showinfo("Успіх", "Запис видалено.")
            except Exception as e:
                messagebox.showerror("Помилка", f"Не вдалося видалити запис: {e}")


# --- ЗАПУСК ДОДАТКА ---
if __name__ == "__main__":
    try:
        from PIL import Image, ImageTk
    except ImportError:
        print("Помилка: Не знайдено бібліотеку Pillow (PIL).")
        print("Будь ласка, встановіть її командою 'pip install Pillow' у вашому віртуальному середовищі.")
    else:
        root = tk.Tk()
        app = StudentDBApp(root)
        root.mainloop()