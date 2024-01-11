import streamlit as st
import pandas as pd

data = pd.read_csv('data.csv')
df = data.copy()

df['genres'] = df['genres'].astype(str) # жанр
df['genres'] = df['genres'].str.replace("['\[\]]", "", regex=True)

def search_books():
    st.title("Поиск книг")
    df_2 = df[['Book-Title', 'Book-Author']].copy()
    df_2.drop_duplicates(inplace=True)
    all_book_titles = df_2['Book-Title'].unique().tolist()
    all_book_authors = df_2['Book-Author'].unique().tolist()
    all_books_and_authors = all_book_titles + all_book_authors
    options = [""] + all_books_and_authors
    search_query = st.selectbox("Введите название книги или автора", options=options)
    if search_query:
        results = df[(df['Book-Title'] == search_query) | (df['Book-Author'] == search_query)]
        results = results.drop_duplicates(subset=['Book-Title', 'Book-Author'])
        # Отображение результатов
        if not results.empty:
            for _, row in results.iterrows():
                st.write(f"**Название:** {row['Book-Title']}")
                st.write(f"**Автор:** {row['Book-Author']}")
                st.write(f"**Год издания:** {row['Year-Of-Publication']}")
                st.write(f"**Серия:** {row['series'] if 'series' in row and pd.notnull(row['series']) else ' '}")
                st.write(
                    f"**Описание:** {row['description'] if 'description' in row and pd.notnull(row['description']) else ' '}")
                st.write(f"**Жанры:** {row['genres'] if 'genres' in row and pd.notnull(row['genres']) else ' '}")
                st.image(row['Image-URL-L'])
                if "saved_books" in st.session_state and row.to_dict() in st.session_state["saved_books"]:
                    if st.button("Удалить из отложенных", key=row['Book-Title']):
                        st.session_state["saved_books"].remove(row.to_dict())
                else:
                    if st.button("Отложить", key=row['Book-Title']):
                        if "saved_books" not in st.session_state:
                            st.session_state["saved_books"] = []
                        st.session_state["saved_books"].append(row.to_dict())
                st.write("---")
        else:
            st.write("Ничего не найдено.")

if __name__ == '__main__':
    search_books()