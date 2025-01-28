import matplotlib.pyplot as plt
import matplotlib.font_manager as ftm
from pathlib import Path

from core.utils.cache import random_cache_path

font = ftm.FontProperties(fname=f'{Path(__file__).resolve().parent}/font/SourceHanSansSC-Regular.otf')

def byte2GB(bytes_list: list):
    return [b / (1024 ** 3) for b in bytes_list]

def single_figure(data: list, yl: str, color: str):
    hours = [f"{h}:00" for h in range(1, 25)]
    figpath = f'{random_cache_path()}.png'
    plt.figure(figsize=(12, 6))

    plt.plot(hours, data, color=color, linestyle='-', alpha=0.5, zorder=1)
    plt.scatter(hours, data, edgecolor=color, facecolor='white', zorder=2)
    plt.fill_between(hours, data, color=color, alpha=0.1)
    plt.ylabel(yl, fontsize=12, fontproperties=font)
    plt.xticks(rotation=45)
    plt.grid(axis='y')
    plt.gca().spines['top'].set_visible(False)
    plt.gca().spines['right'].set_visible(False)
    plt.gca().spines['left'].set_visible(False)
    plt.legend().set_visible(False)

    plt.savefig(figpath)
    return figpath

def complex_figure(data_back: list, yl_back: str, color_back: str,
                   data_front: list, yl_front: str, color_front: str):
    hours = [f"{h}:00" for h in range(1, 25)]
    figpath = f'{random_cache_path()}.png'
    fig, ax_back = plt.subplots(figsize=(12, 6))

    ax_back.plot(hours, data_back, color=color_back, linestyle='-', alpha=0.5, label='Hits', zorder=3)
    ax_back.scatter(hours, data_back, edgecolor=color_back, facecolor='white', zorder=5)
    ax_back.fill_between(hours, data_back, color=color_back, alpha=0.1, zorder=1)
    ax_back.set_ylabel(yl_back, fontsize=12, color='blue')
    ax_back.tick_params(axis='y', labelcolor='blue')

    plt.savefig(figpath)
    return figpath
