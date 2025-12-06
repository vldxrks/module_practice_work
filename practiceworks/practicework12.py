import tkinter as tk
from tkinter import ttk
import math
import random

# --- ГЛОБАЛЬНІ ЗМІННІ ДЛЯ АНІМАЦІЇ (Розділ 6) ---
global Xpos, num, revers, timer_id
num = 0
H = 30
Xpos = 2 * H
Ypos = 180  # Збільшена Ypos для кращої видимості
Hmen = 30
Rhead = 10
Rhead2 = Rhead / 2
revers = 1
L = H * 1.41
timer_id = None
timer_active = False

# --- ЕКВІВАЛЕНТИ RG3 (Стилі кистей) для Розділу 7 ---
BRUSH_STYLES = [
    '',  # 0: bsSolid (Не використовувати stipple)
    'gray25',  # 1: bsCross (25% сірий)
    'half-tone',  # 2: bsDiagCross
    'gray12'  # 3: bsVertical
]


# --- ГЛАВНИЙ КЛАС АБО ФУНКЦІЯ ---
def create_main_app():
    root = tk.Tk()
    root.title("Лабораторна робота: Графіка в Python Tkinter")
    root.geometry("700x500")

    notebook = ttk.Notebook(root)
    notebook.pack(pady=10, padx=10, expand=True, fill="both")

    # --- 1. СТВОРЕННЯ ВКЛАДОК ---

    # Вкладка 1: Стилі ліній (Ми вже реалізували її логіку)
    tab_lines = ttk.Frame(notebook)
    notebook.add(tab_lines, text="Стилі ліній")

    # Вкладка 2: Синусоїди
    tab_sinusoids = ttk.Frame(notebook)
    notebook.add(tab_sinusoids, text="Синусоїди")

    # Вкладка 3: Мультиплікація
    tab_animation = ttk.Frame(notebook)
    notebook.add(tab_animation, text="Мультиплікація")

    # Вкладка 4: Перо і пензель
    tab_penbrush = ttk.Frame(notebook)
    notebook.add(tab_penbrush, text="Перо і пензель")

    # --- 2. КОМПОНЕНТИ ТА ЛОГІКА ДЛЯ КОЖНОЇ ВКЛАДКИ ---

    setup_lines_tab(tab_lines)
    setup_sinusoids_tab(tab_sinusoids)
    setup_animation_tab(root, tab_animation)  # Передаємо root для timer.after
    setup_penbrush_tab(tab_penbrush)

    root.mainloop()


# ----------------------------------------------------------------------
#                         РОЗДІЛ 3: СТИЛІ ЛІНІЙ
# ----------------------------------------------------------------------

root = tk.Tk()
root.title("Лабораторна робота: Стилі ліній")
root.geometry("600x400")

# Створення Canvas (Полотно)
canvas_lines = tk.Canvas(root, bg="white")
# Розміщення полотна: заповнює весь доступний простір
canvas_lines.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)


# --- 2. ФУНКЦІЯ МАЛЮВАННЯ ---

def draw_line_styles():
    """Малює лінії з різними стилями dash на полотні."""

    # 1. Очищення полотна перед малюванням
    canvas_lines.delete("all")

    # 2. Оновлення розмірів для коректного розрахунку ширини
    # Це необхідно, щоб отримати реальну ширину вікна після pack()
    root.update_idletasks()

    # Отримання поточної ширини полотна
    widget_width = canvas_lines.winfo_width()

    # Встановлення базових параметрів
    y_start = 15

    # СТИЛІ ЛІНІЙ:
    # - None: означає суцільну лінію, для якої параметр 'dash' не передається.
    # - Кортежі: задають чергування довжини риски та довжини пробілу (у пікселях).
    styles = [
        None,  # 0: psSolid (Суцільна)
        (5, 5),  # 1: psDash (Рискова)
        (1, 4),  # 2: psDot (Пунктирна)
        (8, 3, 1, 3),  # 3: psDashDot (Риска-крапка)
        (8, 3, 1, 3, 1, 3),  # 4: psDashDotDot (Риска-дві крапки)
        (0, 0),  # 5: psClear (Невидима - тонка лінія без кольору)
        None  # 6: psInsideFrame (Суцільна)
    ]

    style_names = ["Solid (0)", "Dash (1)", "Dot (2)", "DashDot (3)", "DashDotDot (4)", "Clear (5)", "InsideFrame (6)"]

    for i, style in enumerate(styles):
        # Розрахунок Y-координати для кожної лінії
        y = (i + 1) * y_start * 2

        # Словник базових параметрів для create_line
        line_options = {
            "fill": "black",
            "width": 2,
            "tags": "line_style"
        }

        # ❗ ВИПРАВЛЕННЯ TclError:
        # Додаємо параметр 'dash' ТІЛЬКИ якщо це не суцільна лінія (style is not None)
        if style is not None:
            line_options["dash"] = style

        if style == (0, 0):  # Робимо Clear-стиль невидимим
            line_options["fill"] = ""

        # Малювання лінії: розпаковуємо словник line_options
        canvas_lines.create_line(
            0, y, widget_width, y,
            **line_options
        )

        # Додавання назви
        canvas_lines.create_text(widget_width - 150, y, text=style_names[i], anchor="w")


# --- 3. КНОПКА ТА ПРИВ'ЯЗКА ---

# Створення кнопки та прив'язка до функції
button_show = ttk.Button(root, text="Показати Стилі Ліній", command=draw_line_styles)
button_show.pack(pady=10)

# --- 4. ЗАПУСК ГОЛОВНОГО ЦИКЛУ ---
root.mainloop()
# ----------------------------------------------------------------------
#                         РОЗДІЛ 4: СИНУСОЇДИ
# ----------------------------------------------------------------------

def setup_sinusoids_tab(tab):
    # Фрейм для розміщення двох полотен
    canvas_frame = ttk.Frame(tab)
    canvas_frame.pack(pady=10, padx=10, expand=True, fill="both")

    # Ліве полотно: Пікселями (Image4)
    canvas_pixels = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="black")
    canvas_pixels.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)

    # Праве полотно: Пером (Image5)
    canvas_pen = tk.Canvas(canvas_frame, bg="white", highlightthickness=1, highlightbackground="black")
    canvas_pen.pack(side=tk.LEFT, padx=5, expand=True, fill=tk.BOTH)

    def draw_sinusoids():
        canvas_pixels.delete("all")
        canvas_pen.delete("all")

        root.update_idletasks()
        width_pen = canvas_pen.winfo_width()
        height_pen = canvas_pen.winfo_height()

        width_pixels = canvas_pixels.winfo_width()
        height_pixels = canvas_pixels.winfo_height()

        points_pen = []
        Pi = 3.14159

        # Малювання центральної лінії
        canvas_pen.create_line(0, height_pen / 2, width_pen, height_pen / 2, fill="gray")

        for px in range(width_pixels):
            X = px * 4.0 * Pi / width_pixels
            Y = math.sin(X) * 0.9  # Множимо на 0.9, щоб не виходити за межі
            PY = height_pixels - (Y + 1.0) * height_pixels / 2.0

            # Малювання пікселями (Image4)
            if 0 <= PY < height_pixels:
                # Малюємо маленький чорний прямокутник 1x1
                canvas_pixels.create_rectangle(px, PY, px + 1, PY + 1, fill="black", outline="black")

            # Збір точок для малювання пером (Image5)
            points_pen.extend([px, PY])

        # Малювання на правому графіку (Пером)
        # Використовуємо points_pen як список [x1, y1, x2, y2, ...]
        if points_pen:
            canvas_pen.create_line(points_pen, fill="blue", width=2, smooth=True)

    button_draw = ttk.Button(tab, text="Намалювати", command=draw_sinusoids)
    button_draw.pack(pady=10)


# ----------------------------------------------------------------------
#                         РОЗДІЛ 6: МУЛЬТИПЛІКАЦІЯ
# ----------------------------------------------------------------------

def setup_animation_tab(root_win, tab):
    # Оголошуємо canvas_animation як глобальну змінну, щоб вона була доступна у Draw()
    global canvas_animation
    canvas_animation = tk.Canvas(tab, bg="white")
    canvas_animation.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    def Draw():
        global num, Xpos, Ypos, H, Hmen, Rhead, revers, L
        canvas_animation.delete("figure")

        # Малювання "землі" (одноразово)
        if not canvas_animation.find_withtag("ground"):
            canvas_animation.create_line(0, Ypos + 3, canvas_animation.winfo_width(), Ypos + 3,
                                         width=4, fill="darkgreen", tags="ground")

        # Визначаємо координати голови
        if num == 0:
            Yhead = Ypos - H - Hmen
        else:  # num == 1
            Yhead = Ypos - L - Hmen

        # --- Малювання Голови та Капелюха ---
        # Голова (Ellipse)
        canvas_animation.create_oval(Xpos - Rhead, Yhead - 2 * Rhead, Xpos + Rhead, Yhead,
                                     fill="peachpuff", outline="black", tags="figure")
        # Капелюх (Rectangle)
        canvas_animation.create_rectangle(Xpos - Rhead, Yhead - 2 * Rhead - 4, Xpos + Rhead, Yhead - 2 * Rhead - 1,
                                          fill="black", outline="black", tags="figure")

        # Тулуб
        canvas_animation.create_line(Xpos, Ypos - H, Xpos, Yhead, fill="black", tags="figure")

        if num == 0:
            # Рух 0: Ноги згинаються (V-форма)
            canvas_animation.create_line(Xpos - H, Ypos, Xpos, Ypos - H, fill="black", tags="figure")  # Нога 1
            canvas_animation.create_line(Xpos + H, Ypos, Xpos, Ypos - H, fill="black", tags="figure")  # Нога 2

            # Руки (зігнуті)
            canvas_animation.create_line(Xpos, Yhead + 4, Xpos + revers * H, Yhead - H, fill="black",
                                         tags="figure")  # Рука 1
            canvas_animation.create_line(Xpos, Yhead + 4, Xpos + revers * H, Yhead + H, fill="black",
                                         tags="figure")  # Рука 2

            # Малювання "кулаків" (Ellipse)
            canvas_animation.create_oval(Xpos + revers * H - Rhead2, Yhead - H - Rhead2,
                                         Xpos + revers * H + Rhead2, Yhead - H + Rhead2,
                                         fill="red", tags="figure")
            canvas_animation.create_oval(Xpos + revers * H - Rhead2, Yhead + H - Rhead2,
                                         Xpos + revers * H + Rhead2, Yhead + H + Rhead2,
                                         fill="red", tags="figure")


        elif num == 1:
            # Рух 1: Ноги прямі
            canvas_animation.create_line(Xpos, Ypos, Xpos, Yhead, fill="black", tags="figure")  # Тулуб + Ноги прямі

            # Руки (простягнуті)
            canvas_animation.create_line(Xpos, Yhead + 4, Xpos + revers * L, Yhead + 4, fill="black",
                                         tags="figure")  # Рука 1
            # ... (Рука 2 не вказана у VCL коді для case 1, але додамо її симетрично)

            # Кулак
            canvas_animation.create_oval(Xpos + revers * L - Rhead2, Yhead + 4 - Rhead2,
                                         Xpos + revers * L + Rhead2, Yhead + 4 + Rhead2,
                                         fill="red", tags="figure")

    # --- Timer1Timer еквівалент (QTimer) ---
    def timer_tick():
        global Xpos, num, revers, timer_id, timer_active

        # Очищення та перемальовування старого положення не потрібне
        # Tkinter просто малює нове після виклику Draw()

        # 1. Логіка зміни координат і напрямку
        if (Xpos >= canvas_animation.winfo_width() - H) or (Xpos <= H):
            revers = -revers

        # 2. Оновлення координат
        Xpos = Xpos + revers * H
        num = 1 - num

        # 3. Перемальовування
        Draw()

        # 4. Повтор
        if timer_active:
            timer_id = root_win.after(500, timer_tick)

    # --- Обробник кнопки «Пуск/Стоп» (Button7Click) ---
    def start_stop_animation():
        global timer_active, timer_id

        if not canvas_animation.winfo_exists():
            return  # Захист від закриття вікна

        if timer_active:
            # Стоп
            root_win.after_cancel(timer_id)
            timer_active = False
            button_start_stop.config(text="Пуск")
        else:
            # Пуск
            # Ініціалізація та перше малювання
            Draw()
            timer_active = True
            button_start_stop.config(text="Стоп")
            timer_id = root_win.after(500, timer_tick)

    # Ініціалізація: Малюємо початкове положення
    canvas_animation.after(100, Draw)  # Невеликий тайм-аут для коректного отримання розмірів

    button_start_stop = ttk.Button(tab, text="Пуск", command=start_stop_animation)
    button_start_stop.pack(pady=10)


# ----------------------------------------------------------------------
#                         РОЗДІЛ 7: ПЕРО І ПЕНЗЕЛЬ
# ----------------------------------------------------------------------

def setup_penbrush_tab(tab):
    # Оголошення змінних для RadioButtons
    action_var = tk.StringVar(value='0')
    brush_style_var = tk.StringVar(value='0')
    pen_mode_var = tk.StringVar(value='0')

    # Фрейм для розміщення Canvas та елементів керування
    control_frame = ttk.Frame(tab)
    control_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

    canvas_draw = tk.Canvas(tab, bg="white", highlightthickness=1, highlightbackground="black")
    canvas_draw.pack(pady=10, padx=10, fill=tk.BOTH, expand=True)

    # --- Елементи керування (Еквіваленти RG2, RG3, RG4) ---

    # RG2: Дії
    gbox_actions = ttk.LabelFrame(control_frame, text="Дії (RG2)")
    gbox_actions.pack(side=tk.LEFT, padx=5, fill=tk.Y)
    actions = ["Прямокутник", "Еліпс", "Текст", "Заливка (FloodFill)"]
    for i, text in enumerate(actions):
        ttk.Radiobutton(gbox_actions, text=text, variable=action_var, value=str(i)).pack(anchor=tk.W)

    # RG3: Стилі кистей
    gbox_brush = ttk.LabelFrame(control_frame, text="Стилі кистей (RG3)")
    gbox_brush.pack(side=tk.LEFT, padx=5, fill=tk.Y)
    brush_styles = ["Solid", "Cross", "DiagCross", "Vertical"]
    for i, text in enumerate(brush_styles):
        ttk.Radiobutton(gbox_brush, text=text, variable=brush_style_var, value=str(i)).pack(anchor=tk.W)

    # RG4: Режими пера
    gbox_pen = ttk.LabelFrame(control_frame, text="Режими пера (RG4)")
    gbox_pen.pack(side=tk.LEFT, padx=5, fill=tk.Y)
    pen_modes = ["pmCopy", "pmXor", "pmNotXor"]
    for i, text in enumerate(pen_modes):
        # Примітка: Tkinter не має прямого аналога pmXor/pmNotXor
        ttk.Radiobutton(gbox_pen, text=text, variable=pen_mode_var, value=str(i)).pack(anchor=tk.W)

    def button_clear_click():
        canvas_draw.delete("all")
        # Якщо використовувалися складні XOR режими, це може не повністю очистити

    def image_mouse_down(event):
        X, Y = event.x, event.y
        sx = random.randint(30, 100)
        sy = random.randint(30, 100)

        # Випадковий колір
        color_hex = '#%06x' % random.randint(0, 0xFFFFFF)

        # 1. Встановлення стилю кисті (RG3)
        style_index = int(brush_style_var.get())
        brush_stipple = BRUSH_STYLES[style_index]

        # 2. Встановлення режиму пера (RG4)
        pen_mode_index = int(pen_mode_var.get())
        outline_color = "black"
        if pen_mode_index == 1 or pen_mode_index == 2:
            # Для імітації XOR/NotXOR, використовуємо інвертований колір, або залишаємо за замовчуванням
            outline_color = "black"  # або, наприклад, "red"

        # 3. Вибір дії (RG2)
        action_index = int(action_var.get())

        if action_index == 0:  # Прямокутник
            canvas_draw.create_rectangle(X, Y, X + sx, Y + sy,
                                         fill=color_hex,
                                         stipple=brush_stipple if brush_stipple else None,
                                         outline=outline_color)
        elif action_index == 1:  # Еліпс
            canvas_draw.create_oval(X, Y, X + sx, Y + sy,
                                    fill=color_hex,
                                    stipple=brush_stipple if brush_stipple else None,
                                    outline=outline_color)
        elif action_index == 2:  # Текст
            canvas_draw.create_text(X, Y, text="Графіка в С++ Builder",
                                    fill=color_hex,
                                    anchor="nw")
        elif action_index == 3:  # Заливка (FloodFill)
            # У Tkinter немає вбудованого FloodFill. Імітуємо.
            fill_color_hex = '#%02x0000' % random.randint(100, 255)  # Випадковий червоний
            canvas_draw.create_rectangle(X - 50, Y - 50, X + 50, Y + 50,
                                         fill=fill_color_hex,
                                         outline="")

    # Прив'язка обробника миші
    canvas_draw.bind("<Button-1>", image_mouse_down)

    button_clear = ttk.Button(tab, text="Очищення", command=button_clear_click)
    button_clear.pack(pady=10)


# --- ЗАПУСК ПРОГРАМИ ---
if __name__ == "__main__":
    create_main_app()