import streamlit as st
import pandas as pd

data = pd.read_csv('data.csv')
df = data.copy()

# прочитанные книги, отображаются в профиле
def read(user_id):
    books_per_row = st.columns(3)
    user_data = df[df['User-ID'] == int(user_id)]
    sorted_user_data = user_data.sort_values(by='Book-Rating', ascending=False)
    sorted_user_data = sorted_user_data[sorted_user_data['Book-Rating'] != 0]
    unique_user_data = sorted_user_data.drop_duplicates(subset='Book-Title')
    book_titles = unique_user_data['Book-Title'].tolist()
    book_ratings = unique_user_data['Book-Rating'].tolist()
    book_uml = unique_user_data['Image-URL-L'].tolist()
    for i in range(0, len(book_titles), len(books_per_row)):
        for j in range(len(books_per_row)):
            if i + j < len(book_titles):
                with books_per_row[j]:
                    caption = f"{book_titles[i + j]} | {book_ratings[i + j]}"
                    st.image(book_uml[i + j], caption=caption, use_column_width=True)


def show_user_profile():
    st.title('Профиль пользователя')
    if "user_id" not in st.session_state:
        st.session_state["user_id"] = ""
    user_id = st.text_input("Введите id пользователя", st.session_state["user_id"])
    submit = st.button("Войти")
    if submit:
        st.session_state["user_id"] = user_id
        read(user_id)

if __name__ == '__main__':
    show_user_profile()

