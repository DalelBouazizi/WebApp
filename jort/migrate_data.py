import os
import sqlite3
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'myproject.settings')
django.setup()

from articles.models import Article
conn = sqlite3.connect('articles.db')
cursor = conn.cursor()
cursor.execute('SELECT * FROM articles')
resultats = cursor.fetchall()

for row in resultats:
    article = Article(date=row[1], content=row[2], category=row[3])
    article.save()
conn.close()

print("Migration des données terminée avec succès.")
