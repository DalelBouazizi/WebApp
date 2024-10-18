from django.db import models

class Article(models.Model):
    date = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=100, default='General')
    
    def __str__(self):
        return self.content[:50]
