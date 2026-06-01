# Задание 4. Рисование поверх построенного графика.

from datetime import datetime
from pathlib import Path
import tkinter as tk
from tkinter import colorchooser, messagebox
from tkinter import ttk

from PIL import ImageDraw, ImageTk

from data_visual import (
    color_maps,
    columns,
    default_color_map,
    make_visual_image,
)

folder = Path(__file__).resolve().parent
standard_width = 9
standard_color = "#160a60"

x_column = columns[0]
y_column = columns[1]
selected_color_map = default_color_map

paint_mode = False
drawing_line = False
line_color = standard_color
line_width = standard_width

canvas = None
current_image = None
tk_image = None
color_box = None
paint_button = None
color_button = None
width_value = None
x_buttons = {}
y_buttons = {}
before_line_image = None
undo_images = []



def show_image(image):
    global current_image, tk_image
    current_image = image
    tk_image = ImageTk.PhotoImage(image)
    canvas.config(width=image.width, height=image.height)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=tk_image)
    canvas.focus_set()


def refresh_buttons():
    for name, button in x_buttons.items():
        button.config(relief=tk.SUNKEN if name == x_column else tk.RAISED)
    for name, button in y_buttons.items():
        button.config(relief=tk.SUNKEN if name == y_column else tk.RAISED)


def update_graph():
    stop_paint_mode()
    undo_images.clear()
    refresh_buttons()
    show_image(make_visual_image(x_column, y_column, selected_color_map))


def choose_x(name):
    global x_column
    x_column = name
    update_graph()


def choose_y(name):
    global y_column
    y_column = name
    update_graph()


def change_color_map(event=None):
    global selected_color_map
    selected_color_map = color_box.get()
    update_graph()


def switch_paint_mode():
    global paint_mode
    paint_mode = not paint_mode
    if paint_mode:
        paint_button.config(relief=tk.SUNKEN)
        canvas.config(cursor="pencil")
        canvas.focus_set()
    else:
        stop_paint_mode()


def stop_paint_mode(event=None):
    global paint_mode, drawing_line
    paint_mode = False
    drawing_line = False
    if paint_button is not None:
        paint_button.config(relief=tk.RAISED)
    if canvas is not None:
        canvas.config(cursor="")


def choose_color():
    global line_color
    selected = colorchooser.askcolor(color=line_color)[1]
    if selected:
        line_color = selected
        color_button.config(bg=line_color)
    canvas.focus_set()


def draw_square(x, y):
    global current_image, tk_image
    if current_image is None:
        return
    if x < 0 or y < 0 or x >= current_image.width or y >= current_image.height:
        return

    half = max(1, line_width // 2)
    drawer = ImageDraw.Draw(current_image)
    drawer.rectangle((x - half, y - half, x + half, y + half), fill=line_color)
    tk_image = ImageTk.PhotoImage(current_image)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=tk_image)


def start_line(event):
    global drawing_line, before_line_image, line_width
    canvas.focus_set()
    if not paint_mode or current_image is None:
        return
    if event.x < 0 or event.y < 0 or event.x >= current_image.width or event.y >= current_image.height:
        return

    drawing_line = True
    before_line_image = current_image.copy()
    line_width = int(width_value.get())
    draw_square(event.x, event.y)


def continue_line(event):
    if drawing_line and paint_mode:
        draw_square(event.x, event.y)


def finish_line(event=None):
    global drawing_line, before_line_image
    if drawing_line and before_line_image is not None:
        undo_images.append(before_line_image.copy())
    drawing_line = False
    before_line_image = None
    if canvas is not None:
        canvas.focus_set()


def undo_last_line():
    global current_image
    if drawing_line or not undo_images:
        return
    current_image = undo_images.pop()
    show_image(current_image)


def undo_from_event(event=None):
    undo_last_line()
    return "break"


def key_handler(event):
    key = str(event.keysym).lower()
    char = str(getattr(event, "char", "")).lower()
    z_pressed = key in ("z", "я", "cyrillic_ya") or char in ("z", "я")
    modifier_pressed = bool(event.state & 0x4) or bool(event.state & 0x8) or bool(event.state & 0x10) or bool(event.state & 0x100000)
    if z_pressed and modifier_pressed:
        return undo_from_event(event)
    return None


def bind_undo_keys(root):
    key_names = [
        "<Control-z>", "<Control-Z>",
        "<Control-KeyPress-z>", "<Control-KeyPress-Z>",
        "<Command-z>", "<Command-Z>",
        "<Command-KeyPress-z>", "<Command-KeyPress-Z>",
        "<Mod2-KeyPress-z>", "<Mod2-KeyPress-Z>",
        "<Control-KeyPress-Cyrillic_ya>",
        "<Command-KeyPress-Cyrillic_ya>",
        "<Mod2-KeyPress-Cyrillic_ya>",
    ]
    for key_name in key_names:
        try:
            root.bind_all(key_name, undo_from_event)
        except tk.TclError:
            pass
    root.bind_all("<KeyPress>", key_handler)


def save_graph():
    if current_image is None:
        return
    file_name = datetime.now().strftime("graph%H_%M_%S.png")
    current_image.save(folder / file_name)
    messagebox.showinfo("Сохранение", f"График сохранен: {file_name}")
    canvas.focus_set()


def make_y_buttons(parent):
    for name in columns:
        button = tk.Button(parent, text=name, width=24, command=lambda value=name: choose_y(value))
        button.pack(side="top", padx=2, pady=2)
        y_buttons[name] = button


def make_x_buttons(parent):
    first_row = tk.Frame(parent)
    first_row.pack()
    second_row = tk.Frame(parent)
    second_row.pack()
    for index, name in enumerate(columns):
        row = first_row if index < 5 else second_row
        button = tk.Button(row, text=name, width=24, command=lambda value=name: choose_x(value))
        button.pack(side="left", padx=2, pady=2)
        x_buttons[name] = button


def create_window():
    global canvas, color_box, paint_button, color_button, width_value

    root = tk.Tk()
    root.title("Визуализация с ручной разметкой")
    bind_undo_keys(root)

    left = tk.Frame(root)
    left.pack(side="left", padx=8, pady=8, fill="y")
    tk.Label(left, text="Ось Y").pack()
    make_y_buttons(left)

    center = tk.Frame(root)
    center.pack(side="left", padx=8, pady=8)

    top = tk.Frame(center)
    top.pack(pady=4)
    tk.Label(top, text="Цветовая схема").pack(side="left", padx=4)
    color_box = ttk.Combobox(top, values=color_maps, state="readonly", width=18)
    color_box.set(selected_color_map)
    color_box.pack(side="left")
    color_box.bind("<<ComboboxSelected>>", change_color_map)

    canvas = tk.Canvas(center, bg="white", highlightthickness=1, highlightbackground="gray")
    canvas.pack()
    canvas.bind("<Button-1>", start_line)
    canvas.bind("<B1-Motion>", continue_line)
    canvas.bind("<ButtonRelease-1>", finish_line)
    canvas.bind("<Button-3>", stop_paint_mode)

    bottom = tk.Frame(center)
    bottom.pack(pady=6)
    tk.Label(bottom, text="Ось X").pack()
    make_x_buttons(bottom)

    tools = tk.Frame(center)
    tools.pack(pady=5)
    paint_button = tk.Button(tools, text="Рисование", command=switch_paint_mode)
    paint_button.pack(side="left", padx=4)

    color_button = tk.Button(tools, text="  ", width=3, bg=line_color, command=choose_color)
    color_button.pack(side="left", padx=4)

    width_value = tk.StringVar(value=str(line_width))
    tk.Spinbox(tools, from_=1, to=30, width=5, textvariable=width_value).pack(side="left", padx=4)
    tk.Button(tools, text="Сохранить график", command=save_graph).pack(side="left", padx=4)

    update_graph()
    canvas.focus_set()
    root.mainloop()


if __name__ == "__main__":
    create_window()
