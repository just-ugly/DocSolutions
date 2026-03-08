import os
import uuid
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

plt.rcParams["font.sans-serif"] = ["SimHei"]
plt.rcParams["axes.unicode_minus"] = False


# 条形图
def bar_chart(bar_title, x_label, y_label, unit, data):
    """
    生成条形图并返回图片路径

    :param bar_title: 图标题
    :param x_label: 横坐标名称
    :param y_label: 纵坐标名称
    :param unit: 纵坐标单位
    :param data: [{"category": str, "value": number}, ...]
    :return: 图片文件路径
    """

    # 数据安全校验
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("bar_chart: data 不能为空")

    categories = []
    values = []

    for item in data:
        if "category" not in item or "value" not in item:
            raise ValueError("bar_chart: 数据结构错误")
        categories.append(str(item["category"]))
        values.append(float(item["value"]))

    # 创建图表
    plt.figure(figsize=(8, 5))
    bars = plt.bar(categories, values)

    # 标题与坐标轴
    plt.title(bar_title, fontsize=14)
    plt.xlabel(x_label, fontsize=12)

    if unit:
        plt.ylabel(f"{y_label} ({unit})", fontsize=12)
    else:
        plt.ylabel(y_label, fontsize=12)

    # 数值标签
    for bar in bars:
        height = bar.get_height()
        plt.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f"{height}",
            ha="center",
            va="bottom",
            fontsize=10
        )

    plt.tight_layout()

    # ===== 创建 picture 文件夹 =====
    picture_dir = os.path.join(os.getcwd(), "picture")
    os.makedirs(picture_dir, exist_ok=True)

    # ===== 保存文件 =====
    file_name = f"bar_{uuid.uuid4().hex}.png"
    file_path = os.path.join(picture_dir, file_name)

    plt.savefig(file_path, dpi=300)
    plt.close()

    return file_path


# 折线图
def line_chart(line_title, x_label, y_label, unit, data):
    """
    生成折线并返回图片路径

    :param line_title: 图标题
    :param x_label: 横坐标名称
    :param y_label: 纵坐标名称
    :param unit: 纵坐标单位
    :param data: [{"category": str, "value": number}, ...]
    :return: 图片文件路径
    """

    # ===== 数据校验 =====
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("line_chart: data 不能为空")

    categories = []
    values = []

    for item in data:
        if "category" not in item or "value" not in item:
            raise ValueError("line_chart: 数据结构错误")
        categories.append(str(item["category"]))
        values.append(float(item["value"]))

    # ===== 创建图表 =====
    plt.figure(figsize=(8, 5))

    plt.plot(categories, values, marker='o')

    plt.title(line_title, fontsize=14)
    plt.xlabel(x_label, fontsize=12)

    if unit:
        plt.ylabel(f"{y_label} ({unit})", fontsize=12)
    else:
        plt.ylabel(y_label, fontsize=12)

    # 数值标签
    for i, value in enumerate(values):
        plt.text(categories[i], value, f"{value}",
                 ha="center", va="bottom", fontsize=9)

    plt.grid(True, linestyle="--", alpha=0.5)
    plt.tight_layout()

    # ===== 创建 picture 文件夹 =====
    picture_dir = os.path.join(os.getcwd(), "picture")
    os.makedirs(picture_dir, exist_ok=True)

    # ===== 保存文件 =====
    file_name = f"line_{uuid.uuid4().hex}.png"
    file_path = os.path.join(picture_dir, file_name)

    plt.savefig(file_path, dpi=300)
    plt.close()

    return file_path


# 饼图
def pie_chart(pie_title, unit, data):
    """
    生成饼图并返回图片路径
    图片保存在当前目录的 picture 文件夹中

    :param data: [{"category": str, "value": number}, ...]
    """

    # ===== 数据校验 =====
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("pie_chart: data 不能为空")

    labels = []
    values = []

    for item in data:
        if "category" not in item or "value" not in item:
            raise ValueError("pie_chart: 数据结构错误")

        labels.append(str(item["category"]))
        values.append(float(item["value"]))

    total = sum(values)
    if total == 0:
        raise ValueError("pie_chart: 总值不能为0")

    # ===== 创建图表 =====
    plt.figure(figsize=(6, 6))

    def autopct_format(pct):
        absolute = pct * total / 100
        if unit:
            return f"{pct:.1f}%\n({absolute:.1f}{unit})"
        return f"{pct:.1f}%"

    wedges, texts, autotexts = plt.pie(
        values,
        labels=labels,
        autopct=autopct_format,
        startangle=90
    )

    plt.title(pie_title, fontsize=14)
    plt.axis("equal")  # 保证是正圆
    plt.tight_layout()

    # ===== 创建 picture 文件夹 =====
    picture_dir = os.path.join(os.getcwd(), "picture")
    os.makedirs(picture_dir, exist_ok=True)

    file_name = f"pie_{uuid.uuid4().hex}.png"
    file_path = os.path.join(picture_dir, file_name)

    plt.savefig(file_path, dpi=300)
    plt.close()

    return file_path

def scatter_chart(scatter_title, x_label, y_label, unit_x, unit_y, data):
    """
    生成散点图并返回图片路径
    图片保存在当前目录的 picture 文件夹中

    :param data: [{"x": number, "y": number}, ...]
    """

    # ===== 数据校验 =====
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("scatter_chart: data 不能为空")

    x_values = []
    y_values = []

    for item in data:
        if "x" not in item or "y" not in item:
            raise ValueError("scatter_chart: 数据结构错误")

        x_values.append(float(item["x"]))
        y_values.append(float(item["y"]))

    # ===== 创建图表 =====
    plt.figure(figsize=(8, 5))

    plt.scatter(x_values, y_values)

    xlabel = f"{x_label} ({unit_x})" if unit_x else x_label
    ylabel = f"{y_label} ({unit_y})" if unit_y else y_label

    plt.xlabel(xlabel)
    plt.ylabel(ylabel)
    plt.title(scatter_title)

    plt.tight_layout()

    # ===== 创建 picture 文件夹 =====
    picture_dir = os.path.join(os.getcwd(), "picture")
    os.makedirs(picture_dir, exist_ok=True)

    file_name = f"scatter_{uuid.uuid4().hex}.png"
    file_path = os.path.join(picture_dir, file_name)

    plt.savefig(file_path, dpi=300)
    plt.close()

    return file_path

