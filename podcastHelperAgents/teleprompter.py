import sys
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QPushButton, QTextEdit, QInputDialog
from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtCore import QUrl

class Teleprompter(QWidget):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.textEdit = QTextEdit()
        self.loadButton = QPushButton('Load Text')
        self.loadButton.clicked.connect(self.loadText)

        self.webView = QWebEngineView()
        
        layout.addWidget(self.textEdit)
        layout.addWidget(self.loadButton)
        layout.addWidget(self.webView)

        self.setLayout(layout)
        self.setWindowTitle('Teleprompter')
        self.setGeometry(100, 100, 800, 600)

        self.loadHtml()

    def loadText(self):
        text, ok = QInputDialog.getMultiLineText(self, 'Input Dialog', 'Enter your script:')
        if ok:
            self.textEdit.setPlainText(text)
            self.updateTeleprompter()

    def loadHtml(self):
        html_content = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Podcast Teleprompter</title>
            <style>
                body {
                    font-family: Arial, sans-serif;
                    display: flex;
                    justify-content: center;
                    align-items: center;
                    height: 100vh;
                    margin: 0;
                    background-color: #f0f0f0;
                }
                #teleprompter {
                    width: 80%;
                    height: 300px;
                    overflow: hidden;
                    background-color: white;
                    border: 1px solid #ccc;
                    padding: 20px;
                    box-shadow: 0 0 10px rgba(0,0,0,0.1);
                }
                #content {
                    transition: transform 0.5s ease-out;
                }
                #controls {
                    margin-top: 20px;
                    text-align: center;
                }
                button {
                    margin: 0 10px;
                    padding: 10px 20px;
                    font-size: 16px;
                }
            </style>
        </head>
        <body>
            <div>
                <div id="teleprompter">
                    <div id="content"></div>
                </div>
                <div id="controls">
                    <button onclick="adjustSpeed(-0.1)">Slower</button>
                    <button onclick="toggleScrolling()">Start/Stop</button>
                    <button onclick="adjustSpeed(0.1)">Faster</button>
                </div>
            </div>

            <script>
                let content = "Your script will appear here.";
                let scrolling = false;
                let speed = 1;
                const contentElement = document.getElementById('content');
                contentElement.innerHTML = content;

                function toggleScrolling() {
                    scrolling = !scrolling;
                    if (scrolling) {
                        requestAnimationFrame(scroll);
                    }
                }

                function adjustSpeed(change) {
                    speed += change;
                    speed = Math.max(0.1, Math.min(speed, 5));
                }

                function scroll() {
                    if (!scrolling) return;
                    contentElement.style.transform = `translateY(${-window.scrollY}px)`;
                    window.scrollBy(0, speed);
                    if ((window.innerHeight + window.scrollY) >= document.body.offsetHeight) {
                        window.scrollTo(0, 0);
                    }
                    requestAnimationFrame(scroll);
                }

                function updateContent(newContent) {
                    content = newContent;
                    contentElement.innerHTML = content;
                    window.scrollTo(0, 0);  // Reset scroll position
                }
            </script>
        </body>
        </html>
        """
        self.webView.setHtml(html_content)

    def updateTeleprompter(self):
        script = self.textEdit.toPlainText()
        script = script.replace("'", "\\'").replace("\n", "<br>")
        self.webView.page().runJavaScript(f"updateContent('{script}')")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = Teleprompter()
    ex.show()
    sys.exit(app.exec_())