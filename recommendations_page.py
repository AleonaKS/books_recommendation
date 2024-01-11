import pandas as pd
import numpy as np
import streamlit as st
from streamlit import components
from collections import Counter
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


book = pd.read_csv('Books.csv')
user = pd.read_csv('Users.csv')
rating = pd.read_csv('Ratings.csv')
data = pd.read_csv('data.csv')

books = book.copy()
users = user.copy()
ratings = rating.copy()
df = data.copy()
df_copy = df[['Book-Title', 'Image-URL-L', 'series']].copy()


# Топ-10 популярных книг
rating_book = ratings.merge(books,on='ISBN')
rating_book = rating_book[rating_book['Book-Rating'] != 0]
numer_rating = rating_book.groupby(['Book-Title', 'Book-Author']).count()['Book-Rating'].reset_index()
numer_rating.rename(columns={'Book-Rating':'Totle_number_rating'},inplace=True)
avg_rating = rating_book.groupby('Book-Title')['Book-Rating'].mean().reset_index()
avg_rating.rename(columns={'Book-Rating':'Totle_avg_rating'},inplace=True)
popular_df = numer_rating.merge(avg_rating,on='Book-Title')
popular_df = popular_df[popular_df['Totle_number_rating'] >= 250].sort_values('Totle_avg_rating',ascending=False).head(50)
top10 = popular_df.head(10)

df['genres'] = df['genres'].astype(str) # жанр
df['genres'] = df['genres'].str.replace("['\[\]]", "", regex=True)


# для коллаборативной фильтрации
x = ratings['User-ID'].value_counts() > 50
y = x[x].index
rating_with_books = ratings.merge(books, on='ISBN')
number_rating = rating_with_books.groupby('Book-Title')['Book-Rating'].count().reset_index()
number_rating.rename(columns={'Book-Rating': 'number_of_ratings'}, inplace=True)
final_rating = rating_with_books.merge(number_rating, on='Book-Title')
final_rating = final_rating[final_rating['number_of_ratings'] >= 50]
final_rating.drop_duplicates(['User-ID','Book-Title'], inplace=True)
book_pivot = final_rating.pivot_table(columns='User-ID', index='Book-Title', values="Book-Rating")
book_pivot.fillna(0, inplace=True)
similarity_scores = cosine_similarity(book_pivot)


# по описанию
df1 = pd.read_csv('books_1.Best_Books_Ever.csv', low_memory=False)
df2 = df1[['title', 'description', 'series', 'genres']].copy()
df2.dropna(subset=['description'], inplace=True)
df3 = df2[df2['title'].isin(df['Book-Title'])]
count_common_books = df3.shape[0]
df4 = df3.rename(columns={'title': 'Book-Title'})
tfidf = TfidfVectorizer(stop_words='english')
tfidf_matrix = tfidf.fit_transform(df4['description'])
cosine_sim = cosine_similarity(tfidf_matrix, tfidf_matrix)


# коллаборативная фильтрация
def collaborative(book_name):
    try:
        index = np.where(book_pivot.index == book_name)[0][0]
    except IndexError:
        return None
    similar_items = sorted(list(enumerate(similarity_scores[index])), key=lambda x: x[1], reverse=True)[1:4]
    recommended_books = []
    for i in similar_items:
        try:
            temp_df = books[books['Book-Title'] == book_pivot.index[i[0]]]
            recommended_books.extend(list(temp_df.drop_duplicates('Book-Title')['Book-Title'].values))
        except KeyError:
            pass
    return recommended_books


# рекомендации книг из одной серии
def serie(book_name):
    book_series = df_copy.loc[df_copy['Book-Title'] == book_name, 'series'].values
    if book_series.size > 0 and not pd.isnull(book_series[0]):
        other_books_in_series = df_copy[df_copy['series'] == book_series[0]]
        return other_books_in_series['Book-Title'].tolist()
    else:
        return []


# рекомендации книг по похожему описанию
def description(title):
    idx = df4[df4['Book-Title'] == title].index
    if len(idx) > 0:
        idx = idx[0]
        if idx < len(cosine_sim):
            sim_scores = list(enumerate(cosine_sim[idx]))
            sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
            sim_scores = sim_scores[1:4]
            book_indices = [i[0] for i in sim_scores]
            return df4['Book-Title'].iloc[book_indices].tolist()
        else:
            return []
    else:
        return []


# по названиям книг получаем ссылки на обложки и выводим в контейнер
def recommendations(book_titles, recommended_books):
    recommended_books = list(set(recommended_books))
    recommended_books = [book for book in recommended_books if book not in book_titles]
    html_code = """
        <div style="display: flex; flex-direction: row; overflow-x: auto;">
        """
    for book in recommended_books:
        image_url = df.loc[df['Book-Title'] == book, 'Image-URL-L'].values[0]
        html_code += f"""
            <div style="min-width: 200px; margin-right: 2px;">
                <img src="{image_url}" style="width: 80%;">
                <p>{book}</p>
            </div>
            """
    html_code += "</div>"
    components.v1.html(html_code, height=600)


#  страница с рекомендациями
def show_recommendations():
    st.title("Рекомендации")
    user_id = st.session_state["user_id"]
    user_data = df[df['User-ID'] == int(user_id)]
    sorted_user_data = user_data.sort_values(by='Book-Rating', ascending=False)
    unique_user_data = sorted_user_data.drop_duplicates(subset='Book-Title')
    recommend = unique_user_data[unique_user_data['Book-Rating'] > 7]
    book_titles = recommend['Book-Title'].tolist()
    # Популярное
    st.subheader("Популярное")
    top10_books = top10['Book-Title'].values
    recommendations(book_titles, top10_books)
    # коллаборативная фильтрация
    st.subheader("Наши пользователи выбирают")
    recommended_books_collaborative = []
    for title in book_titles:
        books_list = collaborative(title)
        if books_list:
            recommended_books_collaborative.extend(books_list)
    recommendations(book_titles, recommended_books_collaborative)
    # по серии
    st.subheader("Узнайте продолжение истории")
    recommended_books_series = []
    for title in book_titles:
        books_list = serie(title)
        if books_list:
            recommended_books_series.extend(books_list)
    recommendations(book_titles, recommended_books_series)
    # популярное в наиболее читаемом жанре
    st.subheader("Вам может понравится")
    recommend.dropna(subset=['genres'], inplace=True)
    genres_list = recommend['genres'].str.split(',').sum()
    genres_count = Counter(genres_list)
    most_common_genre = genres_count.most_common(2)[1][0]
    filtered_df = df.copy()
    readers_count_filter = filtered_df['Book-Title'].map(filtered_df['Book-Title'].value_counts()) > 25
    genres_filter = filtered_df['genres'].str.contains(most_common_genre)
    result = filtered_df[readers_count_filter & genres_filter].head(10)
    top_books = result.groupby('Book-Title')['Book-Rating'].mean().sort_values(ascending=False).head(10)
    top_books_titles = top_books.index.values
    recommendations(book_titles, top_books_titles)
    # похожие по описанию
    st.subheader("Похожие по сюжету")
    recommended_books_description = []
    for title in book_titles:
        books_list = description(title)
        if books_list:
            recommended_books_description.extend(books_list)
    recommendations(book_titles, recommended_books_description)


if __name__ == '__main__':
    show_recommendations()

    # [254, 1706, 2179, 2198, 2799, 7210, 7346, 8680, 9908, 15408, 16795, 23872, 30081, 32599, 37092, 37235, 38661, 44252,
    #  46461, 47117, 48453, 49460, 52987, 53408, 53510, 54290, 55490, 58730, 60244, 61147, 61257, 61842, 61850, 64922,
    #  65343, 67490, 67547, 68128, 69078, 75485, 76865, 76888, 80071, 80538, 80683, 87473, 87555, 91184, 95359, 100294,
    #  102262, 103636, 104550, 104624, 109779, 111944, 112083, 112953, 119115, 120283, 120515, 121251, 122881, 123298,
    #  123544, 124910, 127813, 128325, 129388, 129716, 130636, 131951, 132684, 133935, 136841, 141070, 144121, 152579,
    #  153475, 154176, 154553, 159033, 160681, 164008, 164533, 164728, 164926, 165576, 166731, 171017, 177432, 178254,
    #  179327, 179791, 189536, 189733, 193248, 194669, 197364, 197823, 207635, 210168, 213638, 215986, 218140, 219683,
    #  224349, 228189, 234597, 236700, 238768, 240541, 240567, 242083, 242639, 244171, 245295, 246759, 252279, 254417,
    #  255347, 257700, 260647, 261825, 263307, 264149, 266840, 267184, 271705, 273159, 273976, 274282, 275520]