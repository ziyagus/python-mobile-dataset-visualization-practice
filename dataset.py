# Задание 1. Загрузка и первичный анализ датасета.

from io import StringIO
from pathlib import Path

import pandas as pd

folder = Path(__file__).resolve().parent
dataset_file = folder / "dataset.csv"
report_file = folder / "report.txt"

df = pd.read_csv(dataset_file)

technical_columns = ["Unnamed: 0"]

numeric_columns = [
    "Screen Size (inches)",
    "RAM (GB)",
    "Storage (GB)",
    "Price (USD)",
    "Rating",
]

category_columns = [
    "Processor",
    "Camera Setup",
]


def make_report():
    lines = []

    lines.append("1. Размер датасета")
    lines.append(str(df.shape))
    lines.append("")

    lines.append("2. Информация о типах данных")
    info = StringIO()
    df.info(buf=info)
    lines.append(info.getvalue().strip())
    lines.append("")

    lines.append("3. Количество пропусков по колонкам")
    lines.append(str(df.isna().sum()))
    lines.append("")

    lines.append("4. Статистика по счетным колонкам")
    lines.append("Колонка> среднее медиана отклонение")
    for column in numeric_columns:
        mean_value = df[column].mean()
        median_value = df[column].median()
        std_value = df[column].std()
        lines.append(f"{column}> {mean_value:.2f}; {median_value:.2f}; {std_value:.2f}")
    lines.append("")

    lines.append("5. Частоты значений по категориальным колонкам")
    for column in category_columns:
        lines.append(f"Категориальная колонка: {column}")
        lines.append(str(df[column].value_counts()))
        lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    text = make_report()
    print(text)
    report_file.write_text(text, encoding="utf-8")
