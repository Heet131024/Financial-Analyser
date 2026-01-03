import sys
import tempfile
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton,
    QListWidget, QFileDialog, QMessageBox, QHBoxLayout,
    QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QUrl
from PyQt5.QtGui import QDesktopServices

from PyPDF2 import PdfMerger, PdfReader


class MergeWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal()
    error = pyqtSignal(str)

    def __init__(self, files, output):
        super().__init__()
        self.files = files
        self.output = output

    def run(self):
        try:
            merger = PdfMerger()
            total = len(self.files)

            for i, pdf in enumerate(self.files):
                merger.append(pdf)
                self.progress.emit(int(((i + 1) / total) * 100))

            with open(self.output, "wb") as f:
                merger.write(f)

            merger.close()
            self.finished.emit()

        except Exception as e:
            self.error.emit(str(e))


class PdfMergerApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("PDF Merger")
        self.setAcceptDrops(True)
        self.resize(650, 450)

        self.layout = QVBoxLayout()
        self.layout.setContentsMargins(8, 8, 8, 8)
        self.layout.setSpacing(6)

        self.list_widget = QListWidget()
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        self.list_widget.setSpacing(3)
        self.list_widget.setMinimumHeight(280)

        self.progress = QProgressBar()
        self.progress.setValue(0)

        btn_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add PDFs")
        self.remove_btn = QPushButton("Remove Selected")
        self.preview_btn = QPushButton("Preview")
        self.merge_btn = QPushButton("Merge PDFs")

        btn_layout.addWidget(self.add_btn)
        btn_layout.addWidget(self.remove_btn)
        btn_layout.addWidget(self.preview_btn)
        btn_layout.addWidget(self.merge_btn)

        self.layout.addWidget(self.list_widget)
        self.layout.addLayout(btn_layout)
        self.layout.addWidget(self.progress)
        self.setLayout(self.layout)

        self.add_btn.clicked.connect(self.add_files)
        self.remove_btn.clicked.connect(self.remove_selected)
        self.preview_btn.clicked.connect(self.preview_merged)
        self.merge_btn.clicked.connect(self.merge_pdfs)

    # ---------- Drag & Drop ----------
    def dragEnterEvent(self, event):
        if event.mimeData().hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event):
        for url in event.mimeData().urls():
            file_path = url.toLocalFile()
            if file_path.lower().endswith(".pdf"):
                pages = self.get_page_count(file_path)
                self.list_widget.addItem(f"{file_path}   [{pages} pages]")

    # ---------- Utilities ----------
    def get_page_count(self, pdf_path):
        try:
            reader = PdfReader(pdf_path)
            return len(reader.pages)
        except Exception:
            return "?"

    # 🔥 PREVIEW MERGED (TEMPORARY)
    def preview_merged(self):
        if self.list_widget.count() < 2:
            QMessageBox.information(
                self, "Preview", "Add at least two PDFs to preview"
            )
            return

        files = [
            self.list_widget.item(i).text().split("   [")[0]
            for i in range(self.list_widget.count())
        ]

        try:
            merger = PdfMerger()

            for pdf in files:
                merger.append(pdf)

            temp_file = tempfile.NamedTemporaryFile(
                delete=False, suffix=".pdf"
            )
            merger.write(temp_file.name)
            merger.close()

            QDesktopServices.openUrl(
                QUrl.fromLocalFile(temp_file.name)
            )

        except Exception as e:
            QMessageBox.critical(self, "Preview Error", str(e))

    # ---------- Buttons ----------
    def add_files(self):
        files, _ = QFileDialog.getOpenFileNames(
            self, "Select PDFs", "", "PDF Files (*.pdf)"
        )
        for f in files:
            pages = self.get_page_count(f)
            self.list_widget.addItem(f"{f}   [{pages} pages]")

    def remove_selected(self):
        for item in self.list_widget.selectedItems():
            self.list_widget.takeItem(self.list_widget.row(item))

    def merge_pdfs(self):
        if self.list_widget.count() < 2:
            QMessageBox.warning(self, "Error", "Add at least two PDFs")
            return

        output, _ = QFileDialog.getSaveFileName(
            self, "Save Merged PDF", "", "PDF Files (*.pdf)"
        )

        if not output:
            return

        files = [
            self.list_widget.item(i).text().split("   [")[0]
            for i in range(self.list_widget.count())
        ]

        self.worker = MergeWorker(files, output)
        self.worker.progress.connect(self.progress.setValue)
        self.worker.finished.connect(self.merge_done)
        self.worker.error.connect(self.merge_error)
        self.worker.start()

    def merge_done(self):
        QMessageBox.information(self, "Success", "PDFs merged successfully!")
        self.progress.setValue(0)

    def merge_error(self, msg):
        QMessageBox.critical(self, "Error", msg)
        self.progress.setValue(0)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PdfMergerApp()
    window.show()
    sys.exit(app.exec_())
