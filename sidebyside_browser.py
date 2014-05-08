import sys
import functools
import urlparse

# from PySide.QtCore import *
from PySide.QtGui import (
    QApplication, QLabel, QHBoxLayout, QVBoxLayout, QWidget, QLineEdit)
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
        pane = QWidget()
        layout = QVBoxLayout()
        pane.setLayout(layout)

        # Create a Label and show it
        label = QLabel(title)
        label.setFixedHeight(32)
        label.show()
        layout.addWidget(label)

        address_bar = QLineEdit()
        layout.addWidget(address_bar)

        web_view = QWebView()
        layout.addWidget(web_view)

        # Attach signal handlers
        address_bar.editingFinished.connect(functools.partial(
            self._addrbar_changed, address_bar, web_view))
        web_view.loadStarted.connect(lambda: label.setText('Loading...'))
        # web_view.loadProgress.connect(
        #     lambda p: label.setText('Loading ({0}%)'.format(p)))
        web_view.titleChanged.connect(label.setText)
        web_view.urlChanged.connect(functools.partial(
            self._url_changed, web_view))
        web_view.urlChanged.connect(
            lambda url: address_bar.setText(url.toString()))

        return {
            'main': pane,
            'layout': layout,
            'title': label,
            'address': address_bar,
            'web_view': web_view,
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
