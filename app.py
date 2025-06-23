import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from wordcloud import WordCloud
from textblob import TextBlob
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem import WordNetLemmatizer

# Download NLTK data
nltk.download('stopwords')
nltk.download('wordnet')
nltk.download('omw-1.4')

# Load data
@st.cache_data
def load_data():
    df = pd.read_csv('dataset/zomato_cafe_reviews.csv')
    df['Overall_Rating'] = df['Overall_Rating'].replace('-', pd.NA)
    df['Overall_Rating'] = pd.to_numeric(df['Overall_Rating'], errors='coerce')
    return df

# Text Preprocessing
stop_words = set(stopwords.words('english'))
lemmatizer = WordNetLemmatizer()

def clean_text(text):
    if pd.isnull(text):
        return ""
    text = re.sub(r'[^a-zA-Z]', ' ', text)
    text = text.lower()
    tokens = text.split()
    tokens = [word for word in tokens if word not in stop_words]
    tokens = [lemmatizer.lemmatize(word) for word in tokens]
    return ' '.join(tokens)

def get_sentiment(text):
    analysis = TextBlob(text)
    polarity = analysis.sentiment.polarity
    if polarity > 0.1:
        return 'Positive'
    elif polarity < -0.1:
        return 'Negative'
    else:
        return 'Neutral'

# Streamlit App
st.title("Zomato Cafe Review Analysis 🍽️")

df = load_data()

tab1, tab2, tab3 = st.tabs(["📊 EDA", "😊 Sentiment Analysis", "☁️ Word Cloud"])

# Tab 1 - EDA
with tab1:
    st.subheader("Rating Distribution")
    sns.countplot(df['Overall_Rating'].dropna())
    st.pyplot(plt.gcf())
    plt.clf()

    st.subheader("Top 10 Cities by Review Count")
    top_cities = df['City'].value_counts().head(10)
    st.bar_chart(top_cities)

    st.subheader("Cuisine Word Frequency")
    all_cuisine = ','.join(df['Cuisine'].dropna().astype(str))
    wordcloud = WordCloud(width=800, height=400).generate(all_cuisine)
    st.image(wordcloud.to_array())

# Tab 2 - Sentiment
with tab2:
    st.subheader("Sentiment Classification")
    df['Clean_Review'] = df['Review'].apply(clean_text)
    df['Sentiment'] = df['Clean_Review'].apply(get_sentiment)
    sentiment_counts = df['Sentiment'].value_counts()
    st.bar_chart(sentiment_counts)

    st.subheader("Average Rating by Sentiment")
    st.dataframe(df.groupby('Sentiment')['Overall_Rating'].mean().reset_index())

# Tab 3 - Word Clouds
with tab3:
    st.subheader("Word Cloud by Sentiment")
    for sentiment in ['Positive', 'Negative', 'Neutral']:
        text = ' '.join(df[df['Sentiment'] == sentiment]['Clean_Review'])
        if text:
            wc = WordCloud(width=800, height=400, background_color='white').generate(text)
            st.image(wc.to_array(), caption=f"{sentiment} Reviews")

