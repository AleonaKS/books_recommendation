import pandas as pd
import streamlit as st

# страница с отложенными пользователем книгами
def show_saved_books():
    st.title("Отложенные книги")
    # Здесь можно добавить контент для страницы с отложенными книгами
    if "saved_books" in st.session_state:
        for book in st.session_state["saved_books"]:
            st.write(f"**Название:** {book['Book-Title']}")
            st.write(f"**Автор:** {book['Book-Author']}")
            st.write(f"**Год издания:** {book['Year-Of-Publication']}")
            st.write(f"**Серия:** {book['series'] if 'series' in book and pd.notnull(book['series']) else ' '}")
            st.write(
                f"**Описание:** {book['description'] if 'description' in book and pd.notnull(book['description']) else ' '}")
            st.write(f"**Жанры:** {book['genres'] if 'genres' in book and pd.notnull(book['genres']) else ' '}")
            st.image(book['Image-URL-L'])
            st.write("---")
    else:
        st.write("У вас пока нет отложенных книг.")

if __name__ == '__main__':
    show_saved_books()