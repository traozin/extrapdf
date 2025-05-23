import sys
import os
from PyQt5.QtCore import QThread, pyqtSignal, QMutex, Qt, QMutex, QMutexLocker, QTimer
from main import extract_text_from_pdf_with_ocr

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QPushButton, QFileDialog, QLabel, QVBoxLayout, QWidget, QProgressBar
)

class PDFProcessorThread(QThread):
    progress = pyqtSignal(int, int)
    finished = pyqtSignal()
    canceled = pyqtSignal()

    def __init__(self, input_dir, output_dir):
        super().__init__()
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.cancel = False
        self.mutex = QMutex()

    def run(self):
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)

        files = [
            file_name for file_name in os.listdir(self.input_dir)
            if file_name.lower().endswith(".pdf")
        ]

        total_files = len(files)

        if total_files == 0:
            self.finished.emit()
            return

        for i, file_name in enumerate(files):
            self.mutex.lock()
            if self.cancel:
                self.canceled.emit()
                self.mutex.unlock()
                return
            self.mutex.unlock()

            pdf_path = os.path.join(self.input_dir, file_name)
            try:
                self.mutex.lock()
                if self.cancel:
                    self.canceled.emit()
                    self.mutex.unlock()
                    return
                self.mutex.unlock()

                extract_text_from_pdf_with_ocr(pdf_path, self.output_dir)
            except Exception as e:
                print(f"Erro ao processar {file_name}: {e}")

            self.progress.emit(int(((i + 1) / total_files) * 100), i + 1)

        self.finished.emit()

    def stop(self):
        with QMutexLocker(self.mutex):
            self.cancel = True

class PDFProcessorApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Processador de PDFs com OCR")
        self.setGeometry(100, 100, 400, 300)

        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()

        self.label = QLabel("Selecione uma pasta com PDFs:", self)
        layout.addWidget(self.label)

        self.selectButton = QPushButton("Selecionar Pasta", self)
        self.selectButton.clicked.connect(self.select_folder)
        layout.addWidget(self.selectButton)

        self.processButton = QPushButton("Processar PDFs", self)
        self.processButton.clicked.connect(self.handle_process_button)
        self.processButton.setEnabled(False)
        layout.addWidget(self.processButton)

        self.progressBar = QProgressBar(self)
        self.progressBar.setValue(0)
        self.progressBar.setVisible(False)
        layout.addWidget(self.progressBar)

        self.statusLabel = QLabel("", self)
        layout.addWidget(self.statusLabel)

        self.timerLabel = QLabel("Tempo decorrido: 00:00:00", self)
        self.timerLabel.setVisible(False)
        layout.addWidget(self.timerLabel)

        self.filesLabel = QLabel("0/0", self)
        self.filesLabel.setAlignment(Qt.AlignRight)
        layout.addWidget(self.filesLabel)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_timer)
        self.elapsed_seconds = 0

    def select_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Selecione uma pasta")
        if folder:
            self.input_folder = folder
            self.label.setText(f"Pasta selecionada: {folder}")

            self.files = [
                file_name for file_name in os.listdir(self.input_folder)
                if file_name.lower().endswith(".pdf")
            ]
            num_files = len(self.files)

            self.filesLabel.setText(f"0/{num_files}")

            if num_files == 0:
                self.processButton.setEnabled(False)
                self.statusLabel.setText("Nenhum arquivo PDF encontrado na pasta.")
            else:
                self.processButton.setEnabled(True)
                self.statusLabel.setText(f"{num_files} arquivos PDF encontrados.")

    def handle_process_button(self):
        if self.processButton.text() == "Processar PDFs":
            self.start_processing()
        else:
            self.cancel_processing()

    def start_processing(self):
        output_dir = os.path.join(self.input_folder, "output")
        self.statusLabel.setText("Processando...")
        self.progressBar.setVisible(True)
        self.timerLabel.setVisible(True)

        self.elapsed_seconds = 0
        self.timer.start(1000)

        self.thread = PDFProcessorThread(self.input_folder, output_dir)
        self.thread.progress.connect(self.update_progress)
        self.thread.finished.connect(self.processing_finished)
        self.thread.canceled.connect(self.processing_canceled)
        self.thread.start()

        self.processButton.setText("Cancelar")
        self.selectButton.setEnabled(False)

    def update_progress(self, value, processed_files):
        self.progressBar.setValue(value)
        self.statusLabel.setText(f"Processando... {processed_files}/{len(self.files)} arquivos concluídos.")
        self.filesLabel.setText(f"{processed_files}/{len(self.files)}")

    def update_timer(self):
        self.elapsed_seconds += 1
        hours, remainder = divmod(self.elapsed_seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        self.timerLabel.setText(f"Tempo decorrido: {hours:02}:{minutes:02}:{seconds:02}")

    def processing_finished(self):
        self.timer.stop()
        self.statusLabel.setText("Processamento concluído!")
        self.reset_ui(keep_timer=True)

    def processing_canceled(self):
        self.timer.stop()
        self.statusLabel.setText("Processamento cancelado!")
        self.reset_ui(keep_timer=False)

    def cancel_processing(self):
        self.thread.stop()
        self.processButton.setEnabled(False)
        self.statusLabel.setText("Cancelando o processamento...")

    def reset_ui(self, keep_timer=False):
        self.progressBar.setVisible(False)
        self.progressBar.setValue(0)
        self.processButton.setText("Processar PDFs")
        self.processButton.setEnabled(True)
        self.selectButton.setEnabled(True)
        if not keep_timer:
            self.timerLabel.setVisible(False)
            self.timerLabel.setText("Tempo decorrido: 00:00:00")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PDFProcessorApp()
    window.show()
    sys.exit(app.exec_())
