import os
import time
import re
import PyPDF2
import sqlite3
import pandas as pd
import numpy as np
import joblib  
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.edge.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.edge.service import Service as EdgeService
from nltk.corpus import stopwords

# Charger le modèle de machine learning et le vectoriseur TF-IDF
model = joblib.load('stacking_model.pkl')
vectorizer = joblib.load('tfidf_vectorizer.pkl')

stop_words = set(stopwords.words('french'))

def preprocess_text(text):
    text = text.lower()
    text = re.sub(r'\d+', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'[^\w\s]', '', text)
    text = ' '.join([word for word in text.split() if word not in stop_words])
    return text

msedge_path = r'C:\Program Files (x86)\msedgedriver.exe'  
options = Options()


dossier_enrg = r'C:\Users\USER\Downloads'
if not os.path.exists(dossier_enrg):
    os.makedirs(dossier_enrg)

options.add_experimental_option('prefs', {
    "download.default_directory": dossier_enrg,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "safebrowsing.enabled": True
})

service = EdgeService(executable_path=msedge_path)
driver = webdriver.Edge(service=service, options=options)

url = "http://www.iort.gov.tn"
driver.get(url)

try:
    frc = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "M32"))
    )
    frc.click()
    print("Bouton français cliqué avec succès.")
    time.sleep(20)
    lien_pdf = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "tzA7"))
    )
    lien_pdf.click()
    print("Bouton PDF cliqué avec succès.")
    time.sleep(50)
   
    pdf_files = [f for f in os.listdir(dossier_enrg) if f.endswith('.pdf')]
    time.sleep(20)
    if not pdf_files:
        raise Exception("Aucun fichier PDF téléchargé trouvé.")
    chemin_complet = os.path.join(dossier_enrg, pdf_files[0])
    print(f"Fichier PDF trouvé : {chemin_complet}")
    time.sleep(20)

except Exception as e:
    print(f"Erreur lors du téléchargement du PDF : {e}")
    driver.quit()
    exit()

finally:
    driver.quit()

def extraire_texte_du_pdf(chemin_pdf):
    with open(chemin_pdf, 'rb') as pdf_file:
        pdf_reader = PyPDF2.PdfReader(pdf_file)
        text = ''
        for page_num in range(1, len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            text += page.extract_text()
        return text

texte_pdf = extraire_texte_du_pdf(chemin_complet)

def extraire_articles(texte):
    articles = []
    current_article = {'date': '', 'content': ''}
    date_pattern = re.compile(r'\d{1,2} [a-zA-Zéû]+ \d{4}')
    lignes = texte.splitlines()
    for ligne in lignes:
        if ligne.startswith('Décret n°') or ligne.startswith('Par arrêté') or ligne.startswith('Chapitre'):
            if current_article['content']:
                articles.append(current_article)
            current_article = {'date': '', 'content': ''}
            current_article['content'] += ligne
        elif date_pattern.search(ligne):
            current_article['date'] = date_pattern.search(ligne).group()
        elif current_article['content']:
            current_article['content'] += '\n' + ligne
    
    if current_article['content']:
        articles.append(current_article)
    return articles

articles = extraire_articles(texte_pdf)


for article in articles:
    preprocessed_text = preprocess_text(article['content'])
    text_vector = vectorizer.transform([preprocessed_text])
    predicted_category = model.predict(text_vector)[0]
    article['category'] = predicted_category

# Connexion à la base de données SQLite
chemin_db = os.path.abspath('articles.db')
conn = sqlite3.connect(chemin_db)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY,          
    date TEXT,
    content TEXT,
    category TEXT
)
''')
conn.commit()

def inserer_article(date, content, category):
    cursor.execute('''
    INSERT INTO articles (date, content, category)
    VALUES (?, ?, ?)
    ''', (date, content, category))
    conn.commit()

# Sauvegarde des articles 
for article in articles:
    inserer_article(article['date'], article['content'], article['category'])

conn.close()
