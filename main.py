# WPU Project
# written in Python3
# written by NiclasVL
from imports import *


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()

        self.updater = QTimer()
        self.updater.timeout.connect(self.updateAll)
        #self.updater.setInterval(int(1/9600))
        self.updater.setSingleShot(False)
        self.updater.start()
        self.initUI()
        self.loadApplications()

    # CONTROLLER
    def start(self):
        self.show()
        return self

    def stop(self):
        with open('applications.pickle', 'wb') as file:
            pickle.dump(self.sliderApps, file)
        self.updateTimer.stop()
        self.windows = None
        self.close()

    def updateAll(self):
        try:
            values = self.getArduinoValues()
            if values is not None:
                self.updateSliderValues(values)
        except Exception as e:
            pass

    # PREPARATIONS
    def initUI(self):
        uic.loadUi('GUI/main.ui', self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())

        self.windows, self.bars, self.percentTexts, self.editButtons = [], [], [], []

        for i in range(5):  # finding and connecting the widgets from the .UI file
            self.bars.append(self.findChild(QProgressBar, f"bar{i}"))
            self.percentTexts.append(self.findChild(QTextEdit, f"text{i}"))
            self.editButtons.append(self.findChild(QPushButton, f"button{i}"))

            self.editButtons[i].clicked.connect(partial(self.button_clicked, i))

    def loadApplications(self):
        self.sliderApps = ["", "", "", ""]
        try:
            with open('applications.pickle', 'rb') as file:
                sliderApps = pickle.load(file)
        except FileNotFoundError:
            sliderApps = ["", "", "", "", ""]
            with open('applications.pickle', 'wb') as file:
                pickle.dump(sliderApps, file)
            print("ERROR: Config file not found; creating a new one.")

        with open('applications.pickle', 'wb') as file: # writing for SysTray
            pickle.dump(sliderApps, file)

        self.sliderApps = sliderApps

    # UI HANDLING
    def button_clicked(self, buttonNumber: int):  # handling of the buttons
        self.windows.append(EditWindow(buttonNumber, self.sliderApps[buttonNumber]))

    def updateSliderValues(self, values):
        for i in range(len(self.bars)):
            self.bars[i].setValue(values[i])

        for i in range(len(self.percentTexts)):
            valuePercent = f"{values[i]}%"
            self.percentTexts[i].clear()
            self.percentTexts[i].setPlainText(str(valuePercent))  # sets the texts to the right percentage

        return values

    def getArduinoValues(self):
        try:
            with open("data.pickle", "rb") as file:
                return pickle.load(file)

        except FileNotFoundError:
            print("SysTray not running")

    # EVENTS
    def closeEvent(self, event):
        with open(f'applications.pickle', 'wb') as file:
            pickle.dump(self.sliderApps, file)

        self.windows = None


class EditWindow(QtWidgets.QDialog):
    def __init__(self, button_number: int, application: str):
        super(EditWindow, self).__init__()
        self.initUI(application)

        self.buttonNumber = button_number

        self.show()

    def initUI(self, application: str):
        uic.loadUi('GUI/edit.ui', self)
        self.setFixedSize(self.geometry().width(), self.geometry().height())

        self.button_apply.clicked.connect(self.apply)
        self.button_discard.clicked.connect(self.discard)
        self.button_file.clicked.connect(self.getFile)
        self.text_app.setText(application)

    def getFile(self):
        dlg = QFileDialog(self)
        dlg.setWindowTitle('Open Executable')
        dlg.setNameFilter('(*.exe)')
        dlg.setFileMode(QtWidgets.QFileDialog.ExistingFile)
        filename = None

        if dlg.exec_() == QtWidgets.QDialog.Accepted:
            filename = str(dlg.selectedFiles()[0]).split("/")[-1]

        self.text_app.setText(filename)

    def apply(self):
        try:
            global window
            # sets the right string for the application that is now selected
            window.sliderApps[self.buttonNumber] = self.text_app.toPlainText().strip()

            saved = False
            while not saved:
                try:
                    with open(f'applications.pickle', 'wb') as file:
                        pickle.dump(window.sliderApps, file)
                    saved = True
                except Exception as e:
                    print(f"{e}")

            self.close()  # closes the popup/window
        except Exception as e:
            print(f"{e}")

    def discard(self):
        self.close()  # closes the popup/window


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
