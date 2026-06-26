# Nama: Farid Nanda Syauqi
# NIM: F1D02310050
# Kelas: C
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QFormLayout, QDialogButtonBox,
    QLineEdit, QTextEdit, QComboBox, QMessageBox
)

class PostDialog(QDialog):
    def __init__(self, parent=None, post=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Post" if post else "Tambah Post")
        self.setMinimumWidth(450)
        
        layout = QVBoxLayout(self)
        form = QFormLayout()
        
        # Input fields
        self.title_input = QLineEdit()
        self.author_input = QLineEdit()
        self.slug_input = QLineEdit()
        self.status_input = QComboBox()
        self.status_input.addItems(["draft", "published"])
        self.body_input = QTextEdit()
        
        # Placeholders
        self.title_input.setPlaceholderText("Wajib diisi")
        self.author_input.setPlaceholderText("Nama penulis/anonim")
        self.slug_input.setPlaceholderText("Slug unik (misal: post-pertama)")
        
        form.addRow("Title *:", self.title_input)
        form.addRow("Author:", self.author_input)
        form.addRow("Slug *:", self.slug_input)
        form.addRow("Status:", self.status_input)
        form.addRow("Body *:", self.body_input)
        layout.addLayout(form)
        
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        
        if post:
            self.title_input.setText(post.get('title', ''))
            self.author_input.setText(post.get('author', ''))
            self.slug_input.setText(post.get('slug', ''))
            self.body_input.setPlainText(post.get('body', ''))
            
            index = self.status_input.findText(post.get('status', 'draft'))
            if index >= 0:
                self.status_input.setCurrentIndex(index)
            
    def accept(self):
        # Validasi dasar di sisi klien
        if not self.title_input.text().strip() or not self.slug_input.text().strip() or not self.body_input.toPlainText().strip():
            QMessageBox.warning(self, "Validasi Gagal", "Title, Slug, dan Body wajib diisi!")
            return
        super().accept()
    
    def get_data(self):
        return {
            'title': self.title_input.text().strip(),
            'author': self.author_input.text().strip(),
            'slug': self.slug_input.text().strip(),
            'status': self.status_input.currentText(),
            'body': self.body_input.toPlainText().strip()
        }