import sys
import functools
import urlparse

# from PySide.QtCore import *
from PySide.QtGui import (
    QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit,
    QPushButton, QSizePolicy)
from PySide.QtWebKit import QWebView


class BrowserApp(object):
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.window = QWidget()
        self.window.resize(1280, 1024)

        self.main_layout = QHBoxLayout()
        self.window.setLayout(self.main_layout)
        self.window.show()

        self.left_pane = self.create_browser_pane('Left')
        self.main_layout.addWidget(self.left_pane['main'])

        self.right_pane = self.create_browser_pane('Right')
        self.main_layout.addWidget(self.right_pane['main'])

        self.panes = [self.left_pane, self.right_pane]

    def run(self):
        self.window.show()
        self.app.exec_()

    def create_browser_pane(self, title):
        # Create the pane widget
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        # Create a label for the title
        title_bar = QLabel("")
        # title_bar.setFixedHeight(32)
        title_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        title_bar.show()
        layout.addWidget(title_bar)

        # Create the "address" box
        address_bar = QLineEdit()
        layout.addWidget(address_bar)

        # todo: we could add some tool buttons here..
        toolbar_layout = QHBoxLayout()
        toolbar = QWidget()
        toolbar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        toolbar.setLayout(toolbar_layout)
        tool_stop = QPushButton()
        tool_stop.setText('Stop')
        toolbar_layout.addWidget(tool_stop)
        tool_back = QPushButton()
        tool_back.setText('Back')
        toolbar_layout.addWidget(tool_back)
        tool_forward = QPushButton()
        tool_forward.setText('Forward')
        toolbar_layout.addWidget(tool_forward)
        tool_reload = QPushButton()
        tool_reload.setText('Reload')
        toolbar_layout.addWidget(tool_reload)
        layout.addWidget(toolbar)

        # Create the web view
        web_view = QWebView()
        web_view.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Expanding)
        layout.addWidget(web_view)

        # Create a status bar
        status_bar = QLabel("")
        status_bar.setFixedHeight(32)
        status_bar.show()
        status_bar.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)
        layout.addWidget(status_bar)

        # Attach signal handlers
        address_bar.editingFinished.connect(functools.partial(
            self._addrbar_changed, address_bar, web_view))

        web_view.loadStarted.connect(
            lambda: status_bar.setText('Loading...'))
        web_view.loadProgress.connect(
            lambda p: status_bar.setText('Loading ({0}%)...'.format(p)))
        web_view.loadFinished.connect(
            lambda p: status_bar.setText('Ready.'.format(p)))
        web_view.statusBarMessage.connect(status_bar.setText)
        web_view.titleChanged.connect(title_bar.setText)
        web_view.urlChanged.connect(functools.partial(
            self._url_changed, web_view))
        web_view.urlChanged.connect(
            lambda url: address_bar.setText(url.toString()))

        # Connect tool buttons
        tool_stop.clicked.connect(web_view.stop)
        tool_back.clicked.connect(web_view.back)
        tool_forward.clicked.connect(web_view.forward)
        tool_reload.clicked.connect(web_view.reload)

        return {
            'main': pane,
            'layout': layout,
            'title': title_bar,
            'address': address_bar,
            'web_view': web_view,
            'status': status_bar,
        }

    def _addrbar_changed(self, addrbar, webview):
        webview.load(addrbar.text())

    def _url_changed(self, webview, qurl):
        """
        The url in a webview just changed: update URLs in other panes as well!
        """

        print("URL Changed -- updating other panes")
        url = urlparse.urlparse(qurl.toString())

        for pane in self.panes:
            if pane['web_view'] is webview:
                continue

            # Update the pane url with path/query/fragment
            try:
                this_pane_url = urlparse.urlparse(
                    pane['web_view'].url().toString())
            except:
                pass  # todo: mark error
            else:
                u = this_pane_url._replace(
                    path=url.path,
                    query=url.query,
                    fragment=url.fragment)
                new_url = urlparse.urlunparse(u)

                # Check here is to prevent bouncing!
                if pane['web_view'].url().toString() != new_url:
                    pane['web_view'].load(new_url)


if __name__ == '__main__':
    app = BrowserApp()
    if len(sys.argv) >= 2:
        app.left_pane['web_view'].load(sys.argv[1])
    if len(sys.argv) >= 3:
        app.right_pane['web_view'].load(sys.argv[2])
    app.run()
