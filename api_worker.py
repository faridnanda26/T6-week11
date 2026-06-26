# api_worker.py
from PySide6.QtCore import QObject, Signal
from api_service import ApiService

class ApiWorker(QObject):
    finished = Signal()
    success = Signal(object)
    error = Signal(str)
    
    def __init__(self, action, post_id=None, title=None, body=None, author=None, slug=None, status=None):
        super().__init__()
        self.action = action
        self.post_id = post_id
        self.title = title
        self.body = body
        self.author = author
        self.slug = slug
        self.status = status
        self.service = ApiService()
    
    def run(self):
        try:
            if self.action == "get_posts":
                result = self.service.get_posts()
            elif self.action == "create_post":
                result = self.service.create_post(self.title, self.body, self.author, self.slug, self.status)
            elif self.action == "update_post":
                result = self.service.update_post(self.post_id, self.title, self.body, self.author, self.slug, self.status)
            elif self.action == "delete_post":
                result = self.service.delete_post(self.post_id)
            else:
                raise ValueError(f"Action tidak dikenali: {self.action}")
            
            self.success.emit(result)
            
        except Exception as e:
            # Mengeluarkan detail JSON error dari server jika ada (sangat berguna untuk error 422)
            if hasattr(e, 'response') and e.response is not None:
                self.error.emit(f"{e}\nDetail Server: {e.response.text}")
            else:
                self.error.emit(str(e))
        finally:
            self.finished.emit()