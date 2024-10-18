import pandas as pd
import numpy as np
import re
import nltk
from nltk.corpus import stopwords
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression 
from sklearn.ensemble import StackingClassifier
from sklearn.metrics import classification_report
from sklearn.utils.class_weight import compute_class_weight
import joblib  


nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

# Charger les données depuis le fichier CSV
df = pd.read_csv('articles.csv')

df['text'] = df['text'].fillna('')

# Prétraitement des données
def preprocess_text(text):
    text = text.lower() 
    text = re.sub(r'\d+', '', text)  
    text = re.sub(r'\s+', ' ', text)  
    text = re.sub(r'[^\w\s]', '', text)  
    text = ' '.join([word for word in text.split() if word not in stop_words])  # Suppression des stop words
    return text

df['processed_text'] = df['text'].apply(preprocess_text)

le = LabelEncoder()
df['label'] = le.fit_transform(df['category'])

num_classes = len(le.classes_)
print(f'Nombre de classes: {num_classes}')

# Diviser les données
train_texts, test_texts, train_labels, test_labels = train_test_split(df['processed_text'], df['label'], test_size=0.2, random_state=42)

vectorizer = TfidfVectorizer(max_features=10000)
X_train = vectorizer.fit_transform(train_texts)
X_test = vectorizer.transform(test_texts)

# Calculer la pondération des classes
class_weights = compute_class_weight('balanced', classes=np.unique(train_labels), y=train_labels)
class_weights_dict = dict(enumerate(class_weights))

# Définir les modèles de base
base_models = [
    ('gb', GradientBoostingClassifier()),
    ('lr', LogisticRegression(class_weight=class_weights_dict, max_iter=1000))
]

# Définir le modèle méta
meta_model = LogisticRegression(max_iter=1000)

# Créer le modèle de stacking
stacking_model = StackingClassifier(estimators=base_models, final_estimator=meta_model)

# Entraîner le modèle de stacking
stacking_model.fit(X_train, train_labels)

# Évaluation du modèle
accuracy = stacking_model.score(X_test, test_labels)
print(f'Test Accuracy: {accuracy}')

# Enregistrer le modèle et le vectorizer
joblib.dump(stacking_model, 'stacking_model.pkl')
joblib.dump(vectorizer, 'vectorizer.pkl')
joblib.dump(le, 'label_encoder.pkl')
