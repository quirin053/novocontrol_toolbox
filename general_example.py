# -*- coding: utf-8 -*-
"""
Created on Mon Feb 17 14:16:14 2025

@author: ge26deb
"""

import matplotlib.pyplot as plt
import pandas as pd
import pathlib
from novo_importer_old import read_novo, parameter_names

# Datei einlesen
messfolder = pathlib.PurePath('I:/BA_Moeller/03_Messergebnisse/032_Messergebnisse/')
messfile = pathlib.PurePath('Novocontrol/20250220/20250220-P8_22-50-70-90DEG_01.TXT')
messpath = messfolder.joinpath(messfile)


df, einheiten = read_novo(messpath)
# Beispiel: Berechnung des Mittelwerts einer Spalte
mean_eps = df["|Eps|"].mean()
print(f"Durchschnittlicher Eps'-Wert: {mean_eps}")

# Freq. Temp. Eps' Eps'' |Eps| Sig' Sig'' |Sig| Tan(Delta) M Temp
parameter_to_plot = "|Sig|"

# Nach Temperaturschritt gruppieren und Plotten
# dft = df.groupby(by="Temp.")
# fig, ax = plt.subplots(figsize=(10, 6))
# ax.set_title(f"{parameter_names[parameter_to_plot]} P8")
# ax.set_xscale('log')
# # ax.set_yscale('log')

# for label, sdf in dft:
#     sdf.plot(x="Freq.", y=parameter_to_plot, ax=ax, label=f"Temp: {label}°C")
#     ax.set_ylabel(f"{parameter_to_plot}  [{einheiten[parameter_to_plot]}]" if einheiten[parameter_to_plot] else parameter_to_plot)

# ax.grid(True)
# ax.set_xlabel("Frequenz")

# Daten plotten
plt.figure(figsize=(10, 6))
plt.plot(df['Freq.'], df[parameter_to_plot], label=parameter_names[parameter_to_plot])
plt.xlabel('Frequenz [Hz]')
plt.ylabel(f"{parameter_to_plot}  [{einheiten[parameter_to_plot]}]" if einheiten[parameter_to_plot] else parameter_to_plot)
plt.title(f"{parameter_names[parameter_to_plot]} über Frequenz")
plt.legend()
plt.grid(True)
plt.xscale('log')
#plt.yscale('log')
plt.show()

# Standard Speicherformat
plt.rcParams['savefig.format'] = 'svg'
