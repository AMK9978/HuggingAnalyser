import random

import pandas as pd
import matplotlib.pyplot as plt

from main import logger


def draw(category):
    file_path = f'identical-{category}.csv'

    df = pd.read_csv(file_path)

    df['size'] = sorted(pd.to_numeric(df['size'], errors='coerce'))
    average_size = df['size'].mean()
    plt.axhline(y=average_size, color='red', linestyle='--', label='Average')

    plt.bar(df.index, df['size'], color='skyblue', edgecolor='black')

    plt.xlabel('Sorted Row Index')
    plt.ylabel('Size in KB (Logarithmic Scale)')
    plt.title(f'Bar Chart of {category.replace("-", " ")}')
    plt.gca().yaxis.get_offset_text().set_visible(True)
    plt.yscale('log')
    plt.savefig(f'{category}_bar_chart.png')
    plt.show()


def draw_without_outliers(category):
    file_path = f'identical-{category}.csv'

    df = pd.read_csv(file_path)

    df['size'] = pd.to_numeric(df['size'], errors='coerce')

    Q1 = df['size'].quantile(0.25)
    Q3 = df['size'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df_no_outliers = df[(df['size'] >= lower_bound) & (df['size'] <= upper_bound)]
    indexes = [index for index, _ in enumerate(df_no_outliers['size'])]
    average_size = df_no_outliers['size'].mean()
    plt.axhline(y=average_size, color='red', linestyle='--', label='Average')

    plt.bar(indexes, sorted(df_no_outliers['size']), color='skyblue', edgecolor='black')

    plt.xlabel('Sorted Row Index')
    plt.ylabel('Size in KB (Logarithmic Scale)')
    plt.title(f'Bar Chart of {category.replace("-", " ")} without outliers')
    plt.gca().yaxis.get_offset_text().set_visible(True)
    plt.yscale('log')

    plt.savefig(f'{category}_without_outlier_bar_chart.png')
    plt.show()


def stat(category):
    file_path = f'identical-{category}.csv'
    df = pd.read_csv(file_path)
    df['size'] = pd.to_numeric(df['size'], errors='coerce')

    mean_size = df['size'].mean()
    std_size = df['size'].std()

    return mean_size, std_size


def stat_without_outliers(category):
    file_path = f'identical-{category}.csv'
    df = pd.read_csv(file_path)

    df['size'] = pd.to_numeric(df['size'], errors='coerce')

    Q1 = df['size'].quantile(0.25)
    Q3 = df['size'].quantile(0.75)
    IQR = Q3 - Q1

    lower_bound = Q1 - 1.5 * IQR
    upper_bound = Q3 + 1.5 * IQR

    df_no_outliers = df[(df['size'] >= lower_bound) & (df['size'] <= upper_bound)]

    mean_size = df_no_outliers['size'].mean()
    std_size = df_no_outliers['size'].std()

    return mean_size, std_size


def stat_without_outliers_std(category):
    file_path = f'identical-{category}.csv'
    df = pd.read_csv(file_path)

    df['size'] = pd.to_numeric(df['size'], errors='coerce')

    mean_size = df['size'].mean()
    std_size = df['size'].std()

    threshold = 3
    df_no_outliers = df[
        (df['size'] > mean_size - threshold * std_size) & (df['size'] < mean_size + threshold * std_size)]

    mean_no_outliers = df_no_outliers['size'].mean()
    std_no_outliers = df_no_outliers['size'].std()

    return mean_no_outliers, std_no_outliers


def draw_categories(categories: list, numbers: list):
    for category in categories:
        number_dict = {}
        for number in numbers:
            file_path = f'models-{category}-{number}.csv'
            df = pd.read_csv(file_path)
            df['number_of_apps'] = pd.to_numeric(df['number_of_apps'], errors='coerce')
            number_dict[number] = df['number_of_apps'].sum()
        color = "#{:06x}".format(random.randint(0, 0xFFFFFF))
        plt.plot(list(number_dict.keys()), list(number_dict.values()), marker='o', linestyle='-', label=category,
                 color=color)
    plt.xlabel('Number of Top Models')
    plt.ylabel('Number of Apps')
    plt.title(f'Line Chart of categories')
    plt.savefig('categories.png')
    plt.legend()
    plt.show()


if __name__ == '__main__':
    draw(category='text-generation')
    draw_without_outliers(category='text-generation')
    mean, std = stat(category='text-generation')
    logger.info(f"{mean}, {std}")
    mean, std = stat_without_outliers(category='text-generation')
    logger.info(f"{mean}, {std}")
    draw(category='text-classification')
    draw_without_outliers(category='text-classification')
    mean, std = stat(category='text-classification')
    logger.info(f"{mean}, {std}")
    mean, std = stat_without_outliers(category='text-classification')
    logger.info(f"{mean}, {std}")
    draw_categories(categories=['text-generation', 'text-classification'], numbers=[20, 30, 40, 50, 60, 100])
