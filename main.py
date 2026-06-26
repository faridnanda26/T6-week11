# main.py
import sys
from PySide6.QtCore import QThread, Qt
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTableWidget, QTableWidgetItem,
    QTextEdit, QSplitter, QHeaderView, QMessageBox, QDialog
)
from dialogs import PostDialog
from api_worker import ApiWorker

class PostViewerApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Posts Manager — SoC Demo")
        self.setGeometry(100, 100, 1000, 650)
        self.posts_data = []
        self._thread = None
        self._worker = None
        self.setup_ui()
        self.fetch_posts()
        
    def setup_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        layout = QVBoxLayout(central)
        
        # State Handling - Status Label
        self.status_label = QLabel("Ready")
        self.status_label.setStyleSheet("font-weight: bold; padding: 4px;")
        layout.addWidget(self.status_label)
        
        btn_layout = QHBoxLayout()
        self.btn_refresh = QPushButton("Refresh")
        self.btn_tambah  = QPushButton("Tambah")
        self.btn_edit    = QPushButton("Edit")
        self.btn_hapus   = QPushButton("Hapus")
        btn_layout.addWidget(self.btn_refresh)
        btn_layout.addWidget(self.btn_tambah)
        btn_layout.addWidget(self.btn_edit)
        btn_layout.addWidget(self.btn_hapus)
        layout.addLayout(btn_layout)
        
        splitter = QSplitter(Qt.Horizontal)
        
        # Tabel dengan 4 Kolom: ID, Title, Author, Status
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(['ID', 'Title', 'Author', 'Status'])
        self.table.setSelectionBehavior(QTableWidget.SelectRows)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(2, 120)
        self.table.setColumnWidth(3, 80)
        splitter.addWidget(self.table)
        
        # Detail Viewer Samping
        self.detail = QTextEdit()
        self.detail.setReadOnly(True)
        splitter.addWidget(self.detail)
        splitter.setSizes([500, 500])
        layout.addWidget(splitter)
        
        # Signals Connection
        self.btn_refresh.clicked.connect(self.fetch_posts)
        self.btn_tambah.clicked.connect(self.add_post)
        self.btn_edit.clicked.connect(self.edit_post)
        self.btn_hapus.clicked.connect(self.delete_post)
        self.table.currentCellChanged.connect(self.on_row_selected)
        
    def run_worker(self, action, on_success, post_id=None, title=None, body=None, author=None, slug=None, status=None):
        """Helper Threading: Menjamin background thread asinkronus bebas kebocoran memori"""
        self._thread = QThread()
        self._worker = ApiWorker(
            action, post_id=post_id, title=title, body=body, 
            author=author, slug=slug, status=status
        )
        self._worker.moveToThread(self._thread)
        
        self._thread.started.connect(self._worker.run)
        self._worker.success.connect(on_success)
        self._worker.error.connect(self.on_error)
        
        # Siklus pembersihan memori aman
        self._worker.finished.connect(self._thread.quit)
        self._worker.finished.connect(self._worker.deleteLater)
        self._thread.finished.connect(self._thread.deleteLater)
        self._worker.finished.connect(lambda: self.set_loading(False))
        
        self.set_loading(True)
        self._thread.start()
        
    def set_loading(self, is_loading):
        """State Handling - Kunci UI saat request sedang aktif"""
        for btn in [self.btn_refresh, self.btn_tambah, self.btn_edit, self.btn_hapus]:
            btn.setEnabled(not is_loading)
        if is_loading:
            self.status_label.setText("Loading data dari server...")
            self.status_label.setStyleSheet("font-weight:bold; color:#3498db; padding:4px;")

    # ===== 1. READ (DAFTAR POSTS) =====
    def fetch_posts(self):
        self.run_worker("get_posts", self.on_posts_loaded)
        
    def on_posts_loaded(self, posts):
        self.posts_data = posts
        self.table.setRowCount(0)
        
        for p in self.posts_data:
            row = self.table.rowCount()
            self.table.insertRow(row)
            self.table.setItem(row, 0, QTableWidgetItem(str(p['id'])))
            self.table.setItem(row, 1, QTableWidgetItem(p.get('title', '')))
            self.table.setItem(row, 2, QTableWidgetItem(p.get('author') or 'Anonymous'))
            self.table.setItem(row, 3, QTableWidgetItem(p.get('status', 'draft')))
            
        self.status_label.setText(f"{len(posts)} posts berhasil dimuat")
        self.status_label.setStyleSheet("font-weight:bold; color:#27ae60; padding:4px;")
        
    # ===== 2. DETAIL POST (TERMASUK COMMENTS) =====
    def on_row_selected(self, row, col, prev_row, prev_col):
        if row < 0 or row >= len(self.posts_data):
            return
        p = self.posts_data[row]
        
        # Membaca list komentar jika disediakan oleh struktur API
        comments_list = p.get('comments', [])
        comments_str = ""
        if comments_list:
            for idx, c in enumerate(comments_list, 1):
                comments_str += f"  {idx}. {c.get('user', 'Anon')}: {c.get('text', '')}\n"
        else:
            comments_str = "  (Tidak ada komentar)"

        self.detail.setPlainText(
            f"=== DETAIL POST ===\n"
            f"ID       : {p.get('id')}\n"
            f"Title    : {p.get('title')}\n"
            f"Author   : {p.get('author') or 'Anonymous'}\n"
            f"Slug     : {p.get('slug')}\n"
            f"Status   : {p.get('status')}\n"
            f"-----------------------------------------\n"
            f"CONTENT:\n{p.get('body')}\n"
            f"-----------------------------------------\n"
            f"COMMENTS:\n{comments_str}"
        )
        
    # ===== 3. TAMBAH POST =====
    def add_post(self):
        dialog = PostDialog(self)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.run_worker(
                "create_post", self.on_post_created,
                title=data['title'], body=data['body'], author=data['author'],
                slug=data['slug'], status=data['status']
            )
            
    def on_post_created(self, result):
        new_id = result.get('data', {}).get('id', 'Unknown')
        QMessageBox.information(self, "Sukses", f"Post baru sukses dibuat! ID Server: {new_id}")
        self.fetch_posts()
        
    # ===== 4. EDIT POST =====
    def edit_post(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post di tabel yang ingin diubah!")
            return
        post = self.posts_data[row]
        dialog = PostDialog(self, post)
        if dialog.exec() == QDialog.Accepted:
            data = dialog.get_data()
            self.run_worker(
                "update_post", self.on_post_updated,
                post_id=post['id'], title=data['title'], body=data['body'], 
                author=data['author'], slug=data['slug'], status=data['status']
            )
            
    def on_post_updated(self, result):
        QMessageBox.information(self, "Sukses", "Post berhasil diperbarui di server!")
        self.fetch_posts()
        
    # ===== 5. HAPUS POST (CASCADE) =====
    def delete_post(self):
        row = self.table.currentRow()
        if row < 0:
            QMessageBox.warning(self, "Peringatan", "Pilih post yang ingin dihapus!")
            return
        post_id = self.posts_data[row]['id']
        reply = QMessageBox.question(
            self, "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus post ID {post_id}?\nAll comments linked to this post will be permanently deleted.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            self.run_worker("delete_post", self.on_post_deleted, post_id=post_id)
            
    def on_post_deleted(self, result):
        QMessageBox.information(self, "Sukses", "Post dan seluruh komentarnya berhasil dihapus!")
        self.fetch_posts()
        
    # ===== ERROR HANDLING STATE =====
    def on_error(self, message):
        self.status_label.setText("Gagal memproses request.")
        self.status_label.setStyleSheet("font-weight:bold; color:#e74c3c; padding:4px;")
        QMessageBox.critical(self, "API Error / Validasi Gagal", message)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = PostViewerApp()
    window.show()
    sys.exit(app.exec())