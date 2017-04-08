import sys
from PyQt4.QtGui import QWidget, QApplication, QMainWindow
from PyQt4.QtWebKit import QWebView
from PyQt4.QtCore import QSize, QUrl


class WebWidget(QWidget):
    def __init__(self, parent=None):
        super(WebWidget, self).__init__(parent)
        self.web = QWebView()
        self.web.setMinimumSize(QSize(500, 500))
        self.web.setUrl(QUrl(r'http://www.google.com/'))
        # self.resize(500, 500)


class MainWindow(QMainWindow):
    def __init__(self):
        super(MainWindow, self).__init__()
        self.resize(500, 500)
        # self.web_widget = WebWidget(self)
        self.web = QWebView()
        self.web.setMinimumSize(QSize(500, 500))
        self.web.setUrl(QUrl(r'http://www.google.com/'))
        self.setCentralWidget(self.web)
        self.setWindowTitle("Web")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())