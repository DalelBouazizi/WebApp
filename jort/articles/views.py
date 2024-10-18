from django.shortcuts import render, get_object_or_404, redirect
from .models import Article
import joblib
import re
import nltk
from nltk.corpus import stopwords

# les chemins vers les fichiers de modèles
MODEL_PATH = 'C:/Users/USER/Desktop/myproject/models/stacking_model.pkl'
VECTORIZER_PATH = 'C:/Users/USER/Desktop/myproject/models/vectorizer.pkl'
LABEL_ENCODER_PATH = 'C:/Users/USER/Desktop/myproject/models/label_encoder.pkl'
stacking_model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)
le = joblib.load(LABEL_ENCODER_PATH)


nltk.download('stopwords')
stop_words = set(stopwords.words('french'))

def clean_text(text):
    text = text.lower()  
    text = re.sub(r'\d+', '', text)  
    text = re.sub(r'\s+', ' ', text)  
    text = re.sub(r'[^\w\s]', '', text)  
    text = ' '.join([word for word in text.split() if word not in stop_words])  # Suppression des stop words
    return text


def classifier_article(content):
    processed_content = clean_text(content)
    vectorized_content = vectorizer.transform([processed_content])
    predicted_label = stacking_model.predict(vectorized_content)
    predicted_category = le.inverse_transform(predicted_label)[0]
    print(f"Catégorie prédite : {predicted_category}")  # Log pour vérifier la catégorie prédite
    return predicted_category
def liste_articles(request):
    query_date = request.GET.get('date')
    query_category = request.GET.get('category')
    articles = Article.objects.all()
    if query_date:
        articles = articles.filter(date__icontains=query_date)
    
    if query_category:
        articles = articles.filter(category__icontains=query_category)

    if request.method == 'POST':
        for article in articles:
            category_key = f'category_{article.id}'
            new_category = request.POST.get(category_key)
            if new_category:
                article.category = new_category
                article.save()
    return render(request, 'articles/liste_articles.html', {'articles': articles, 'query_date': query_date, 'query_category': query_category})
def delete_article(request, article_id):
    article = get_object_or_404(Article, id=article_id)
    if request.method == "POST":
        article.delete()
        return redirect('liste_articles')
    
def add_article(request):
    if request.method == 'POST':
        content = request.POST.get('content')
        date = request.POST.get('date')
        category = classifier_article(content)
        
        new_article = Article(date=date, content=content, category=category)
        new_article.save()
        return redirect('liste_articles')
    return render(request, 'articles/add_article.html')
def contact(request):
    return render(request, 'articles/contact.html')