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

def complex_figure(data_bottom: list, yl_bottom: str, color_bottom: str,
                   data_top: list, yl_top: str, color_top: str):
    hours = [f"{h}:00" for h in range(1, 25)]
    figpath = f'{random_cache_path()}.png'
    fig, ax_bottom = plt.subplots(figsize=(18, 6))
    ax_top = ax_bottom.twinx()

    ax_bottom.plot(hours, data_bottom, color=color_bottom, linestyle='-', alpha=0.5, label='Hits', zorder=3)
    ax_bottom.scatter(hours, data_bottom, edgecolor=color_bottom, facecolor='white', zorder=5)
    ax_bottom.fill_between(hours, data_bottom, color=color_bottom, alpha=0.1, zorder=1)
    ax_bottom.set_ylabel(yl_bottom, fontsize=12, fontproperties=font)

    ax_top.plot(hours, data_top, color=color_top, linestyle='-', alpha=0.5, label='Hits', zorder=3)
    ax_top.scatter(hours, data_top, edgecolor=color_top, facecolor='white', zorder=5)
    ax_top.fill_between(hours, data_top, color=color_top, alpha=0.1, zorder=1)
    ax_top.set_ylabel(yl_top, fontsize=12, fontproperties=font)

    ax_bottom.legend().set_visible(False)
    ax_top.legend().set_visible(False)
    ax_bottom.spines['top'].set_visible(False)
    ax_top.spines['top'].set_visible(False)
    ax_bottom.spines['left'].set_visible(False)
    ax_top.spines['left'].set_visible(False)
    ax_bottom.spines['right'].set_visible(False)
    ax_top.spines['right'].set_visible(False)

    plt.savefig(figpath)
    return figpath
