# api_service.py
import requests

class ApiService:
    BASE_URL = "https://api.pahrul.my.id/api"
    TIMEOUT = 10
    
    def get_posts(self):
        """GET /api/posts - Ambil semua posts"""
        response = requests.get(f"{self.BASE_URL}/posts", timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json().get('data', [])
    
    def create_post(self, title, body, author, slug, status):
        """POST /api/posts - Tambah post baru"""
        payload = {
            'title': title,
            'body': body,
            'author': author,
            'slug': slug,
            'status': status
        }
        response = requests.post(f"{self.BASE_URL}/posts", json=payload, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()
    
    def update_post(self, post_id, title, body, author, slug, status):
        """PUT /api/posts/{id} - Update data post lengkap"""
        payload = {
            'title': title,
            'body': body,
            'author': author,
            'slug': slug,
            'status': status
        }
        response = requests.put(f"{self.BASE_URL}/posts/{post_id}", json=payload, timeout=self.TIMEOUT)
        response.raise_for_status()
        return response.json()
    
    def delete_post(self, post_id):
        """DELETE /api/posts/{id} - Hapus post (Cascade delete diurus backend)"""
        response = requests.delete(f"{self.BASE_URL}/posts/{post_id}", timeout=self.TIMEOUT)
        response.raise_for_status()
        return True