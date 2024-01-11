import streamlit as st
from recommendations_page import show_recommendations
from search_books_page import search_books
from saved_books_page import show_saved_books
from profile_page import show_user_profile


# Страницы
pages = {
    "Профиль": show_user_profile,
    "Рекомендации": show_recommendations,
    "Поиск книг": search_books,
    "Отложенные книги": show_saved_books,
}

# Панель с переключением между страницами
page_selection = st.sidebar.radio("Выберите страницу", list(pages.keys()))
# Вызов функции соответствующей выбранной странице
pages[page_selection]()



