# WPU Project
# written in Python3
# written by NiclasVL
from imports import *  # importiert alle Bibliotheken


class Window(QtWidgets.QMainWindow):  # Main-Window Classe
    def __init__(self):
        super(Window, self).__init__()  # initialisiert das window

        # initialisiert den Loop
        self.updater = QTimer()
        self.updater.timeout.connect(self.updateAll)
        self.updater.setSingleShot(False)
        self.updater.start()

        self.initUI()  # initialisert die UI
        self.loadApplications()  # lädt die Programme

    # CONTROLLER
    def start(self):  # startet alles
        self.show()
        return self

    def stop(self):  # stoppt alles
        with open('applications.pickle', 'wb') as file:  # speichert die Programme in eine Datei
            pickle.dump(self.sliderApps, file)
        self.updateTimer.stop()  # stoppt den Loop
        self.windows = None  # schließt alle popups
        self.close()  # schließt Main-Window

    def updateAll(self):  # Loop
        try:
            values = self.getArduinoValues()  # lädt Daten aus einer Datei
            if values is not None:  # falls Daten da sind
                self.updateSliderValues(values)  # updatet UI
        except Exception as e:
            pass

    # PREPARATIONS
    def initUI(self):
        uic.loadUi('GUI/main.ui', self)  # lädt UI aus einer Datei
        self.setFixedSize(self.geometry().width(), self.geometry().height())  # setzt die Dimensionen

        self.windows, self.bars, self.percentTexts, self.editButtons = [], [], [], []

        for i in range(5):  # Finden und Verbinden der Widgets aus der .UI-Datei
            self.bars.append(self.findChild(QProgressBar, f"bar{i}"))
            self.percentTexts.append(self.findChild(QTextEdit, f"text{i}"))
            self.editButtons.append(self.findChild(QPushButton, f"button{i}"))

            self.editButtons[i].clicked.connect(partial(self.button_clicked, i))

    def loadApplications(self):  # lädt die Programme
        self.sliderApps = ["", "", "", ""]  # Default
        try:  # versucht aus der Datei zu laden
            with open('applications.pickle', 'rb') as file:
                sliderApps = pickle.load(file)
        except FileNotFoundError:  # wenn die Datei nicht gefunden wird
            sliderApps = ["", "", "", "", ""]
            with open('applications.pickle', 'wb') as file:  # speichert das Default ab
                pickle.dump(sliderApps, file)
            print("ERROR: Config file not found; creating a new one.")

        with open('applications.pickle', 'wb') as file: # schreibt es für SysTray
            pickle.dump(sliderApps, file)

        self.sliderApps = sliderApps

    # UI HANDLING
    def button_clicked(self, buttonNumber: int):  # Bedienung der Tasten
        self.windows.append(EditWindow(buttonNumber, self.sliderApps[buttonNumber]))

    def updateSliderValues(self, values):  # updatet die Sliders
        for i in range(len(self.bars)):
            self.bars[i].setValue(values[i])

        for i in range(len(self.percentTexts)):  # Die Texte unter den Slidern
            valuePercent = f"{values[i]}%"
            self.percentTexts[i].clear()  # löscht was zuvor dadrin war
            self.percentTexts[i].setPlainText(str(valuePercent))  # setzt die Texte auf den richtigen Prozentwert

        return values

    def getArduinoValues(self):
        try:
            with open("data.pickle", "rb") as file:
                return pickle.load(file)  # lädt die Daten von dem SysTray

        except FileNotFoundError:
            print("SysTray not running")

    # EVENTS
    def closeEvent(self, event):
        with open(f'applications.pickle', 'wb') as file:
            pickle.dump(self.sliderApps, file)  # beim schließen die Programme abspeichern

        self.windows = None


class EditWindow(QtWidgets.QDialog):  # Popup fürs Editieren von den Programmen
    def __init__(self, button_number: int, application: str):
        super(EditWindow, self).__init__()  # intialisiert das Fenster
        self.initUI(application)  # lädt die UI

        self.buttonNumber = button_number  # nummer der slider

        self.show()  # startet alles

    def initUI(self, application: str):
        uic.loadUi('GUI/edit.ui', self) # lädt die UI von einer .UI Datei
        self.setFixedSize(self.geometry().width(), self.geometry().height())  # setzt die Geometrie/Größe

        # verbinden der Buttons zu Funktionen
        self.button_apply.clicked.connect(self.apply)
        self.button_discard.clicked.connect(self.discard)
        self.button_file.clicked.connect(self.getFile)

        self.text_app.setText(application)  # setzt den Text zum derzeitigen Programm

    def getFile(self):  # öffnet einen FileDialog
        dlg = QFileDialog(self)
        dlg.setWindowTitle('Open Executable')
        dlg.setNameFilter('(*.exe)')  # nur .exe Dateien
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        filename = None

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            filename = str(dlg.selectedFiles()[0]).split("/")[-1]  # nimmt den Dateinamen

        self.text_app.setText(filename)  # setzt ihn zu den text

    def apply(self):
        try:
            global window
            # setzt die richtigen String für die jetzt ausgewählte Anwendung
            window.sliderApps[self.buttonNumber] = self.text_app.toPlainText().strip()

            saved = False
            while not saved:
                try:
                    with open(f'applications.pickle', 'wb') as file:
                        pickle.dump(window.sliderApps, file)  # speichert die Programme
                    saved = True
                except Exception as e:
                    print(f"{e}")

            self.close()  # schließt das popup
        except Exception as e:
            print(f"{e}")

    def discard(self):
        self.close()  # schließt das popup ohne zu speichern


def main():
    app = QtWidgets.QApplication(argv)
    window = Window()
    window.start()
    app.exec_()

if __name__ == '__main__':
    app = QtWidgets.QApplication(argv)
    window = Window()
    window.start()
    app.exec_()
