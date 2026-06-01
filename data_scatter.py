# Задание 2. Первичная точечная диаграмма.

from datetime import datetime
from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import messagebox

from PIL import Image, ImageTk
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import dataset

folder = Path(__file__).resolve().parent
marker_style = "d"
columns = dataset.numeric_columns

x_column = columns[0]
y_column = columns[1]

canvas = None
current_image = None
tk_image = None
x_buttons = {}
y_buttons = {}


def figure_to_image(figure):
    buffer = BytesIO()
    figure.subplots_adjust(left=0.13, right=0.96, top=0.9, bottom=0.15)
    FigureCanvasAgg(figure).print_png(buffer)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def make_scatter_image(x_name, y_name):
    figure = Figure(figsize=(7.8, 5.2), dpi=100)
    plot = figure.add_subplot(111)

    plot.scatter(
        dataset.df[x_name],
        dataset.df[y_name],
        marker=marker_style,
        alpha=0.7,
        edgecolors="black",
        linewidths=0.25,
    )
    plot.set_title("Точечная диаграмма")
    plot.set_xlabel(x_name)
    plot.set_ylabel(y_name)
    plot.grid(True)

    return figure_to_image(figure)


def show_image(image):
    global current_image, tk_image
    current_image = image
    tk_image = ImageTk.PhotoImage(image)
    canvas.config(width=image.width, height=image.height)
    canvas.delete("all")
    canvas.create_image(0, 0, anchor="nw", image=tk_image)


def refresh_buttons():
    for name, button in x_buttons.items():
        button.config(relief=tk.SUNKEN if name == x_column else tk.RAISED)
    for name, button in y_buttons.items():
        button.config(relief=tk.SUNKEN if name == y_column else tk.RAISED)


def update_graph():
    refresh_buttons()
    show_image(make_scatter_image(x_column, y_column))


def choose_x(name):
    global x_column
    x_column = name
    update_graph()


def choose_y(name):
    global y_column
    y_column = name
    update_graph()


def save_graph():
    if current_image is None:
        return
    file_name = datetime.now().strftime("graph%H_%M_%S.png")
    current_image.save(folder / file_name)
    messagebox.showinfo("Сохранение", f"График сохранен: {file_name}")


def make_column_buttons(parent, command, storage, side):
    for name in columns:
        button = tk.Button(parent, text=name, width=22, command=lambda value=name: command(value))
        button.pack(side=side, padx=3, pady=3)
        storage[name] = button


def create_window():
    global canvas

    root = tk.Tk()
    root.title("Первичная визуализация данных")

    left = tk.Frame(root)
    left.pack(side="left", padx=8, pady=8, fill="y")
    tk.Label(left, text="Ось Y").pack()
    make_column_buttons(left, choose_y, y_buttons, "top")

    center = tk.Frame(root)
    center.pack(side="left", padx=8, pady=8)
    canvas = tk.Canvas(center, bg="white")
    canvas.pack()

    bottom = tk.Frame(center)
    bottom.pack(pady=6)
    tk.Label(bottom, text="Ось X").pack()
    x_area = tk.Frame(bottom)
    x_area.pack()
    make_column_buttons(x_area, choose_x, x_buttons, "left")

    tk.Button(center, text="Сохранить график", command=save_graph).pack(pady=5)
    update_graph()
    root.mainloop()


if __name__ == "__main__":
    create_window()
