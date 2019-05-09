import json

import pandas as pd
from matplotlib import cbook
from matplotlib.ticker import NullFormatter
from scipy.stats.stats import pearsonr


import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

def scatter_plot(data_points, ):
    df = pd.DataFrame(data_points)
    sns.pairplot(df, kind="reg")
    plt.show()


def main():
    result_file = open('result.json', 'r')
    result = json.load(result_file)

    edu_item_name = set()
    corpus_name = set()

    for item in result['rows']:
        for name in item['edu_info']:
            edu_item_name.add(name)
        for name in item['word_choice']:
            corpus_name.add(name)


    edu_points = {}
    word_choice_points = {}

    for item in result['rows']:
        for name in edu_item_name:
            try:
                edu_points[name].append(item['edu_info'][name])
            except:
                try:
                    edu_points[name] = [item['edu_info'][name]]
                except:
                    edu_points[name] = None
        for name in corpus_name:
            try:
                word_choice_points[name].append(item['word_choice'][name])
            except:
                try:
                    word_choice_points[name] = [item['word_choice'][name]]
                except:
                    word_choice_points[name] = None

    print(word_choice_points)
    print(edu_points)

    correlation_result = {}
    for edu_name, x_list in edu_points.items():
        for corpus_name, y_list in word_choice_points.items():
            valid_x = x_list
            valid_y = y_list
            if x_list and y_list:
                for i in range(len(x_list)):
                    if x_list[i] is None or y_list is None:
                        valid_x.pop(i)
                        valid_y.pop(i)
                data_points = []
                for i in range(len(valid_x)):
                    data_points.append([valid_x[i],valid_y[i]])
                scatter_plot(data_points)
                correlation_result[(edu_name,corpus_name)] = pearsonr(x_list,y_list)
    print(correlation_result)

    for key, value in correlation_result.items():
        if value[0] >= 0.5:
            print(key, ": ", value)


if __name__ == '__main__':
    main()