# Imports from internal Python Libraries
from functools import partial
from time import sleep
import pickle, threading, serial, pythoncom
from sys import argv

# Imports from external Python Libraries
import serial.tools.list_ports
from PyQt5 import QtWidgets, uic, QtCore
from PyQt5.QtCore import QTimer
from PyQt5.QtWidgets import QProgressBar, QTextEdit, QPushButton, QFileDialog
from pycaw.pycaw import AudioUtilities, ISimpleAudioVolume
from infi.systray import SysTrayIcon
import ctypes