# Imports from internal Python Libraries
from functools import partial
from time import sleep  # wird benutzt um eine bestimmte Zeit zu warten
import pickle  # wird benutzt um Dateien einfach zu speichern
import threading  # wird für Threads benutzt
import serial  # wird für das zugreifen auf den serriellen Port benutzt
import pythoncom 
from sys import argv  # wenn extra Argumente vorhanden sind

# Imports from external Python Libraries
import serial.tools.list_ports  # wird benutzt um den Seriellen Port zu finden
# PyQt5 ist die Fenster-Bibliothek
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QProgressBar, QTextEdit, QPushButton, QFileDialog
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from infi.systray import SysTrayIcon  # wird benutzt um den SysTray zu erzeugen
import ctypes  # wird benutzt um einen Thread zu stoppen