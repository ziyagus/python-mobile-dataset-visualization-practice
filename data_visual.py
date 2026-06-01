# Задание 3. Расширенная визуализация данных.

from datetime import datetime
from io import BytesIO
from pathlib import Path
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

from PIL import Image, ImageTk
from matplotlib import colormaps
from matplotlib.backends.backend_agg import FigureCanvasAgg
from matplotlib.figure import Figure

import dataset

folder = Path(__file__).resolve().parent
marker_style = "d"
default_color_map = "magma"

numeric_columns = dataset.numeric_columns
category_columns = dataset.category_columns
columns = numeric_columns + category_columns

color_maps = [
    "viridis", "plasma", "inferno", "magma", "cividis",
    "Greys", "Purples", "Blues", "Greens", "Oranges",
    "Reds", "YlOrBr", "YlOrRd", "OrRd", "PuRd",
    "RdPu", "BuPu", "GnBu", "PuBu", "YlGnBu",
    "PuBuGn", "BuGn", "YlGn", "binary", "gist_yarg",
    "spring", "summer", "autumn", "winter",
]

x_column = columns[0]
y_column = columns[1]
selected_color_map = default_color_map

canvas = None
current_image = None
tk_image = None
x_buttons = {}
y_buttons = {}
color_box = None


def make_colors(color_name, count):
    color_map = colormaps[color_name]
    if count <= 1:
        return [color_map(0.65)]
    return [color_map(0.2 + 0.7 * index / (count - 1)) for index in range(count)]


def figure_to_image(figure, bottom=0.18):
    buffer = BytesIO()
    figure.subplots_adjust(left=0.14, right=0.96, top=0.9, bottom=bottom)
    FigureCanvasAgg(figure).print_png(buffer)
    buffer.seek(0)
    return Image.open(buffer).convert("RGB")


def make_visual_image(x_name, y_name, color_name=default_color_map):
    figure = Figure(figsize=(8.2, 5.4), dpi=100)
    plot = figure.add_subplot(111)

    x_numeric = x_name in numeric_columns
    y_numeric = y_name in numeric_columns
    x_category = x_name in category_columns
    y_category = y_name in category_columns

    if x_numeric and y_numeric and x_name == y_name:
        plot.hist(
            dataset.df[x_name].dropna(),
            bins=10,
            color=colormaps[color_name](0.65),
            edgecolor="black",
        )
        plot.set_title(f"Гистограмма: {x_name}")
        plot.set_xlabel(x_name)
        plot.set_ylabel("Количество записей")
        plot.grid(True, axis="y")
        return figure_to_image(figure)

    if x_category and y_category and x_name == y_name:
        counts = dataset.df[x_name].value_counts().head(10)
        plot.pie(
            counts.values,
            labels=counts.index.astype(str),
            autopct="%1.1f%%",
            colors=make_colors(color_name, len(counts)),
        )
        plot.set_title(f"Круговая диаграмма: {x_name}")
        return figure_to_image(figure, bottom=0.08)

    if x_category:
        counts = dataset.df[x_name].value_counts().head(12)
        plot.bar(
            counts.index.astype(str),
            counts.values,
            color=make_colors(color_name, len(counts)),
            edgecolor="black",
        )
        plot.set_title(f"Столбчатая диаграмма: {x_name}")
        plot.set_xlabel(x_name)
        plot.set_ylabel("Количество записей")
        plot.tick_params(axis="x", labelrotation=35)
        plot.grid(True, axis="y")
        return figure_to_image(figure, bottom=0.3)

    if x_numeric and y_category:
        top_values = dataset.df[y_name].value_counts().head(10).index
        data_groups = []
        labels = []
        for value in top_values:
            values = dataset.df.loc[dataset.df[y_name] == value, x_name].dropna()
            if len(values) > 0:
                data_groups.append(values)
                labels.append(str(value))

        box = plot.boxplot(data_groups, tick_labels=labels, patch_artist=True)
        for patch, color in zip(box["boxes"], make_colors(color_name, len(data_groups))):
            patch.set_facecolor(color)
        plot.set_title(f"Коробочная диаграмма: {x_name} по {y_name}")
        plot.set_xlabel(y_name)
        plot.set_ylabel(x_name)
        plot.tick_params(axis="x", labelrotation=35)
        plot.grid(True, axis="y")
        return figure_to_image(figure, bottom=0.3)

    values = dataset.df[y_name] if y_numeric else None
    plot.scatter(
        dataset.df[x_name],
        dataset.df[y_name],
        c=values,
        cmap=color_name if y_numeric else None,
        marker=marker_style,
        alpha=0.72,
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
    show_image(make_visual_image(x_column, y_column, selected_color_map))


def choose_x(name):
    global x_column
    x_column = name
    update_graph()


def choose_y(name):
    global y_column
    y_column = name
    update_graph()


def change_color(event=None):
    global selected_color_map
    selected_color_map = color_box.get()
    update_graph()


def save_graph():
    if current_image is None:
        return
    file_name = datetime.now().strftime("graph%H_%M_%S.png")
    current_image.save(folder / file_name)
    messagebox.showinfo("Сохранение", f"График сохранен: {file_name}")


def make_buttons(parent, command, storage, side):
    for name in columns:
        button = tk.Button(parent, text=name, width=24, command=lambda value=name: command(value))
        button.pack(side=side, padx=2, pady=2)
        storage[name] = button


def create_window():
    global canvas, color_box

    root = tk.Tk()
    root.title("Расширенная визуализация данных")

    left = tk.Frame(root)
    left.pack(side="left", padx=8, pady=8, fill="y")
    tk.Label(left, text="Ось Y").pack()
    make_buttons(left, choose_y, y_buttons, "top")

    center = tk.Frame(root)
    center.pack(side="left", padx=8, pady=8)

    top = tk.Frame(center)
    top.pack(pady=4)
    tk.Label(top, text="Цветовая схема").pack(side="left", padx=4)
    color_box = ttk.Combobox(top, values=color_maps, state="readonly", width=18)
    color_box.set(selected_color_map)
    color_box.pack(side="left")
    color_box.bind("<<ComboboxSelected>>", change_color)

    canvas = tk.Canvas(center, bg="white")
    canvas.pack()

    bottom = tk.Frame(center)
    bottom.pack(pady=6)
    tk.Label(bottom, text="Ось X").pack()
    first_row = tk.Frame(bottom)
    first_row.pack()
    second_row = tk.Frame(bottom)
    second_row.pack()
    for index, name in enumerate(columns):
        row = first_row if index < 5 else second_row
        button = tk.Button(row, text=name, width=24, command=lambda value=name: choose_x(value))
        button.pack(side="left", padx=2, pady=2)
        x_buttons[name] = button

    tk.Button(center, text="Сохранить график", command=save_graph).pack(pady=5)
    update_graph()
    root.mainloop()


if __name__ == "__main__":
    create_window()
