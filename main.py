"""
Random Password Generator
Author: [Ваше Имя Фамилия]
Version: 1.0.0
Description: GUI-приложение для генерации случайных паролей с настройками и историей
"""

import tkinter as tk
from tkinter import ttk, messagebox
import random
import string
import json
import os
from datetime import datetime


class PasswordGenerator:
    """Главный класс приложения для генерации паролей"""

    def __init__(self, root):
        self.root = root
        self.root.title("Генератор паролей - Password Generator")
        self.root.geometry("750x600")
        self.root.resizable(True, True)

        # Центрирование окна
        self.center_window()

        # Переменные для настроек
        self.password_length = tk.IntVar(value=12)
        self.use_lowercase = tk.BooleanVar(value=True)
        self.use_uppercase = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_special = tk.BooleanVar(value=True)

        # История паролей
        self.history_file = "password_history.json"
        self.history = []

        # Создание интерфейса
        self.create_widgets()

        # Загрузка сохранённой истории
        self.load_history()

        # Обновление отображения истории
        self.update_history_display()

        # Генерация первого пароля
        self.generate_password()

    def center_window(self):
        """Центрирование окна на экране"""
        self.root.update_idletasks()
        width = 750
        height = 600
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f'{width}x{height}+{x}+{y}')

    def create_widgets(self):
        """Создание всех элементов интерфейса"""

        # Основной контейнер
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)

        # ===== Блок генерации пароля =====
        gen_frame = ttk.LabelFrame(main_frame, text="Генерация пароля", padding="10")
        gen_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        # Длина пароля
        length_frame = ttk.Frame(gen_frame)
        length_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=5)

        ttk.Label(length_frame, text="Длина пароля:").pack(side=tk.LEFT, padx=(0, 10))

        self.length_scale = ttk.Scale(
            length_frame, from_=4, to=32, orient=tk.HORIZONTAL,
            variable=self.password_length, command=self.update_length_label
        )
        self.length_scale.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        self.length_label = ttk.Label(length_frame, text="12", width=5)
        self.length_label.pack(side=tk.LEFT)

        # Чекбоксы для выбора символов
        chars_frame = ttk.Frame(gen_frame)
        chars_frame.grid(row=1, column=0, pady=10)

        ttk.Checkbutton(
            chars_frame, text="Строчные буквы (a-z)",
            variable=self.use_lowercase
        ).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(
            chars_frame, text="Заглавные буквы (A-Z)",
            variable=self.use_uppercase
        ).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(
            chars_frame, text="Цифры (0-9)",
            variable=self.use_digits
        ).pack(side=tk.LEFT, padx=5)

        ttk.Checkbutton(
            chars_frame, text="Спецсимволы (!@#$%^&*)",
            variable=self.use_special
        ).pack(side=tk.LEFT, padx=5)

        # Кнопка генерации
        self.generate_btn = ttk.Button(
            gen_frame, text="🔐 Сгенерировать пароль",
            command=self.generate_password
        )
        self.generate_btn.grid(row=2, column=0, pady=10)

        # Поле сгенерированного пароля
        password_frame = ttk.Frame(gen_frame)
        password_frame.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=10)

        ttk.Label(password_frame, text="Сгенерированный пароль:").pack(side=tk.LEFT, padx=(0, 10))

        self.password_var = tk.StringVar()
        self.password_entry = ttk.Entry(
            password_frame, textvariable=self.password_var,
            font=("Courier", 12), width=30
        )
        self.password_entry.pack(side=tk.LEFT, padx=(0, 10), fill=tk.X, expand=True)

        self.copy_btn = ttk.Button(
            password_frame, text="📋 Копировать",
            command=self.copy_to_clipboard
        )
        self.copy_btn.pack(side=tk.LEFT)

        # ===== Блок истории =====
        history_frame = ttk.LabelFrame(main_frame, text="История паролей", padding="10")
        history_frame.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))

        # Создание таблицы
        columns = ("Дата", "Пароль", "Длина", "Сложность")
        self.tree = ttk.Treeview(history_frame, columns=columns, show="headings", height=10)

        # Настройка колонок
        self.tree.heading("Дата", text="Дата создания")
        self.tree.heading("Пароль", text="Пароль")
        self.tree.heading("Длина", text="Длина")
        self.tree.heading("Сложность", text="Сложность")

        self.tree.column("Дата", width=150)
        self.tree.column("Пароль", width=200)
        self.tree.column("Длина", width=60)
        self.tree.column("Сложность", width=80)

        # Скроллбар
        scrollbar = ttk.Scrollbar(history_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))

        history_frame.columnconfigure(0, weight=1)
        history_frame.rowconfigure(0, weight=1)

        # ===== Кнопки управления историей =====
        history_buttons = ttk.Frame(main_frame)
        history_buttons.grid(row=2, column=0, sticky=(tk.W, tk.E), pady=(0, 10))

        ttk.Button(
            history_buttons, text="🗑 Очистить историю",
            command=self.clear_history
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            history_buttons, text="💾 Сохранить историю",
            command=self.save_history
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            history_buttons, text="📊 Статистика",
            command=self.show_statistics
        ).pack(side=tk.LEFT, padx=5)

        # Статусная строка
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            main_frame, textvariable=self.status_var,
            relief=tk.SUNKEN, anchor=tk.W
        )
        status_bar.grid(row=3, column=0, sticky=(tk.W, tk.E), pady=(5, 0))

        # Настройка растягивания для main_frame
        main_frame.rowconfigure(1, weight=1)

    def update_length_label(self, event=None):
        """Обновление метки длины пароля"""
        self.length_label.config(text=str(self.password_length.get()))

    def get_character_pool(self):
        """Получение набора символов на основе выбранных опций"""
        chars = ""

        if self.use_lowercase.get():
            chars += string.ascii_lowercase
        if self.use_uppercase.get():
            chars += string.ascii_uppercase
        if self.use_digits.get():
            chars += string.digits
        if self.use_special.get():
            chars += "!@#$%^&*"

        return chars

    def calculate_strength(self, password):
        """Расчёт сложности пароля"""
        score = 0
        if len(password) >= 12:
            score += 2
        elif len(password) >= 8:
            score += 1

        if any(c.islower() for c in password):
            score += 1
        if any(c.isupper() for c in password):
            score += 1
        if any(c.isdigit() for c in password):
            score += 1
        if any(c in "!@#$%^&*" for c in password):
            score += 2

        if score >= 6:
            return "Очень высокий"
        elif score >= 4:
            return "Высокий"
        elif score >= 3:
            return "Средний"
        elif score >= 2:
            return "Низкий"
        else:
            return "Очень низкий"

    def generate_password(self):
        """Генерация случайного пароля"""
        # Валидация: проверка выбранных опций
        if not (self.use_lowercase.get() or self.use_uppercase.get() or
                self.use_digits.get() or self.use_special.get()):
            messagebox.showwarning("Ошибка", "Выберите хотя бы один тип символов!")
            return

        length = self.password_length.get()

        # Валидация: проверка длины
        if length < 4:
            messagebox.showwarning("Ошибка", "Минимальная длина пароля - 4 символа!")
            self.password_length.set(4)
            length = 4
        elif length > 32:
            messagebox.showwarning("Ошибка", "Максимальная длина пароля - 32 символа!")
            self.password_length.set(32)
            length = 32

        chars = self.get_character_pool()

        # Генерация пароля
        password = ''.join(random.choice(chars) for _ in range(length))

        # Добавление хотя бы одного символа из каждого выбранного типа
        password_list = list(password)
        index = 0
        if self.use_lowercase.get() and not any(c.islower() for c in password_list):
            password_list[0] = random.choice(string.ascii_lowercase)
            index += 1
        if self.use_uppercase.get() and not any(c.isupper() for c in password_list):
            password_list[index % length] = random.choice(string.ascii_uppercase)
            index += 1
        if self.use_digits.get() and not any(c.isdigit() for c in password_list):
            password_list[index % length] = random.choice(string.digits)
            index += 1
        if self.use_special.get() and not any(c in "!@#$%^&*" for c in password_list):
            password_list[index % length] = random.choice("!@#$%^&*")

        random.shuffle(password_list)
        password = ''.join(password_list)

        # Сохранение в историю
        strength = self.calculate_strength(password)
        self.add_to_history(password, strength)

        # Отображение пароля
        self.password_var.set(password)

        # Обновление статуса
        self.status_var.set(f"Пароль сгенерирован (длина: {length}, сложность: {strength})")

    def add_to_history(self, password, strength):
        """Добавление пароля в историю"""
        entry = {
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "password": password,
            "length": len(password),
            "strength": strength
        }
        self.history.append(entry)
        self.update_history_display()
        self.save_history()

    def update_history_display(self):
        """Обновление отображения истории"""
        if not hasattr(self, 'tree'):
            return

        for item in self.tree.get_children():
            self.tree.delete(item)

        for entry in reversed(self.history[-50:]):
            self.tree.insert("", tk.END, values=(
                entry["date"],
                entry["password"],
                entry["length"],
                entry["strength"]
            ))

    def copy_to_clipboard(self):
        """Копирование пароля в буфер обмена"""
        password = self.password_var.get()
        if password:
            self.root.clipboard_clear()
            self.root.clipboard_append(password)
            self.status_var.set("Пароль скопирован в буфер обмена!")
            messagebox.showinfo("Успех", "Пароль скопирован в буфер обмена!")
        else:
            messagebox.showwarning("Ошибка", "Нет пароля для копирования!")

    def clear_history(self):
        """Очистка истории"""
        if messagebox.askyesno("Подтверждение", "Вы уверены, что хотите очистить всю историю?"):
            self.history = []
            self.update_history_display()
            self.save_history()
            self.status_var.set("История очищена")

    def save_history(self):
        """Сохранение истории в JSON файл"""
        try:
            with open(self.history_file, 'w', encoding='utf-8') as f:
                json.dump(self.history, f, ensure_ascii=False, indent=2)
        except Exception as e:
            messagebox.showerror("Ошибка", f"Не удалось сохранить историю: {str(e)}")

    def load_history(self):
        """Загрузка истории из JSON файла"""
        if os.path.exists(self.history_file):
            try:
                with open(self.history_file, 'r', encoding='utf-8') as f:
                    self.history = json.load(f)
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось загрузить историю: {str(e)}")
                self.history = []
        else:
            self.history = []

    def show_statistics(self):
        """Отображение статистики по паролям"""
        if not self.history:
            messagebox.showinfo("Статистика", "История пуста. Сгенерируйте несколько паролей для статистики.")
            return

        total = len(self.history)
        avg_length = sum(entry["length"] for entry in self.history) / total

        strength_counts = {}
        for entry in self.history:
            strength = entry["strength"]
            strength_counts[strength] = strength_counts.get(strength, 0) + 1

        stats = f"""📊 Статистика использования:

Общее количество паролей: {total}
Средняя длина: {avg_length:.1f} символов

Распределение по сложности:"""

        for strength, count in strength_counts.items():
            percentage = (count / total) * 100
            stats += f"\n  • {strength}: {count} ({percentage:.1f}%)"

        messagebox.showinfo("Статистика", stats)


def main():
    """Главная функция запуска приложения"""
    root = tk.Tk()
    app = PasswordGenerator(root)
    root.mainloop()


if __name__ == "__main__":
    main()