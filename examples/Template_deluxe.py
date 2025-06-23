import matplotlib.pyplot as plt
import pandas as pd
import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent / "src")) # add path to toolbox
from novocontrol_toolbox import novo_toolbox as nt
from itertools import cycle, islice
import re

basepath = pathlib.Path(__file__).parent.parent / "tests/testdata"

x6 = nt.MeasurementGroup.from_files(basepath, ['20250303/20250303-X6_20DEG_01_scrambled.txt', '20250303/20250303-X6_20DEG_02_scrambled.txt', '20250303/20250303-X6_20DEG_03_scrambled.txt'])
x6.plot_kwargs['color'] = '#0065BD'
x7 = nt.MeasurementGroup.from_files(basepath, ['20250217/20250217-X7_20DEG_01_scrambled.txt', '20250217/20250217-X7_20DEG_02_scrambled.txt', '20250217/20250217-X7_20DEG_03_scrambled.txt', '20250217/20250217-X7_20DEG_04_scrambled.txt'])
x7.plot_kwargs['color'] = '#E37222'

# for presentation
plt.rcParams.update({'font.size': 14})
plt.rcParams['lines.linewidth'] = 2

# Freq. Temp. Eps' Eps'' |Eps| Sig' Sig'' |Sig| Tan(Delta) M Temp
parameter_to_plot = "Tan(Delta)"
parameter_to_plot = "|Sig|"
parameter_to_plot = "Sig'"
parameter_to_plot = "|Eps|"

master_messung = x6[0]
plot_title ="x6 and x7"


objects_to_plot = [x6, x7]


plottype = 'custom'
plottype = 'mean'
plottype = 'mean_bounds'
plottype = 'single'

zoomin = True
zoomin = False

fig, ax = plt.subplots(figsize=(10, 6))
ax.set_title(f"{nt.parameter_names[parameter_to_plot]} {plot_title}")
ax.set_xscale('log')
if parameter_to_plot in ["|Sig|", "Sig'"]:
    ax.set_yscale('log')


def plot_objects(objects, ax, plottype, parameter_to_plot, **kwargs):
    colorlist = cycle(['tab:blue', 'tab:orange', 'tab:green', 'tab:red', 'tab:purple', 'tab:brown', 'tab:pink', 'tab:gray'])
    colorlist = cycle(['#0065BD', '#E37222', '#A2AD00', '#98C6EA', '#DAD7CB']) # TUM colors
    for i in objects:
        if plottype == 'mean_bounds':
            i.plot_mean_bounds(parameter_to_plot, ax, color=next(colorlist), ignore_negatives=True)
        elif plottype == 'mean':
            i.mean().plot(parameter_to_plot, ax, color=next(colorlist), **kwargs)
        elif plottype == 'single':
            if isinstance(i, nt.MeasurementGroup):
                i.plot_singles(parameter_to_plot, ax, colors=list(islice(colorlist, len(i.measurements))), **kwargs)
            elif isinstance(i, nt.Measurement):
                i.plot(parameter_to_plot, ax, color=next(colorlist), **kwargs)
            
plot_objects(objects_to_plot, ax, plottype, parameter_to_plot)


if zoomin:
    # Zoom region
    x1, x2, y1, y2 = 10, 10.8, 1.03e-11, 1.12e-11  # subregion of the original image

    axins = ax.inset_axes(
        [0.65, 0.2, 0.3, 0.3],
        xlim=(x1, x2), ylim=(y1, y2))
    ax.indicate_inset_zoom(axins, edgecolor="black")

    plot_objects(objects_to_plot, axins, plottype, parameter_to_plot)

    axins.legend().remove()

if parameter_to_plot == "Tan(Delta)":
    ax.set_ylabel(r"$\tan(\delta)$" + (f" [{master_messung.einheiten[parameter_to_plot]}]" if master_messung.einheiten[parameter_to_plot] else ""))
else:
    ax.set_ylabel(f"{parameter_to_plot}  [{master_messung.einheiten[parameter_to_plot]}]" if master_messung.einheiten[parameter_to_plot] else parameter_to_plot)
ax.grid(True)
ax.set_xlabel("Frequenz [Hz]")


output_path = pathlib.PurePath('your/path')

plt.rcParams['savefig.format'] = 'pdf' # use pdf for latex
plt.rcParams['savefig.directory'] = output_path
plt.tight_layout()


autoexport = True
autoexport = False

export_parameters = ["|Eps|", "Tan(Delta)", "|Sig|", "Sig'"]

def clean_filename(s):
    # strip invalid symbols
    s = s.replace("''", "i").replace("'", "r")
    s = re.sub(r'[\\/*?:"<>|]', "", s)
    return s

if autoexport and parameter_to_plot in export_parameters:
    fname = f"{plot_title}_{parameter_to_plot}"
    fname = clean_filename(fname)
    output_file = output_path / f"{fname}.pdf"
    plt.savefig(output_file, bbox_inches="tight")

plt.show()