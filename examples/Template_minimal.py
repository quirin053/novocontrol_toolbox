import matplotlib.pyplot as plt
import sys
import pathlib
import sys
sys.path.append(str(pathlib.Path(__file__).parent.parent / "src")) # add path to toolbox
from novocontrol_toolbox import novo_toolbox as nt

basepath = pathlib.Path(__file__).parent.parent / "tests/testdata/20250303"

x6 = nt.MeasurementGroup.from_files(basepath, ['20250303-X6_20DEG_01_scrambled.txt', '20250303-X6_20DEG_02_scrambled.txt', '20250303-X6_20DEG_03_scrambled.txt'])
x6.group_Name = 'X6'

fig, ax = plt.subplots(figsize=(10, 6))

x6.plot_mean_bounds("|Eps|", ax=ax)

ax.grid()
ax.set_xlabel('Frequenz [Hz]')
ax.set_ylabel('|Eps|')
ax.set_xscale('log')

plt.show()
