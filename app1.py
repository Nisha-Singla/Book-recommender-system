

import streamlit as st
import pickle
import numpy as np
from difflib import get_close_matches

# -------------------
# Load data
# -------------------
pt = pickle.load(open("pt.pkl", "rb"))                    # pivot table index = Book-Title
books = pickle.load(open("books.pkl", "rb"))              # full books dataframe
similarity_scores = pickle.load(open("similarity_scores.pkl", "rb"))
popular_df = pickle.load(open("popular.pkl", "rb"))       # top 50 popular books (num_ratings, avg_rating, etc)

# -------------------
# Utility functions
# -------------------
def recommend(book_name, n=5):
    """Return a list of dicts with recommendation info for given book_name."""
    if not book_name or not book_name.strip():
        return []
    book_name = book_name.strip().lower()
    title_map = {title.lower(): title for title in pt.index}
    matches = get_close_matches(book_name, title_map.keys(), n=1, cutoff=0.55)
    if not matches:
        return []

    matched_title = title_map[matches[0]]
    try:
        idx = np.where(pt.index == matched_title)[0][0]
    except IndexError:
        return []

    sim_scores = list(enumerate(similarity_scores[idx]))
    sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)[1 : n + 1]

    recs = []
    for i, score in sim_scores:
        title = pt.index[i]
        # fetch one representative row from books
        row = books[books["Book-Title"] == title].drop_duplicates("Book-Title").iloc[0]
        recs.append(
            {
                "title": row["Book-Title"],
                "author": row.get("Book-Author", "Unknown"),
                "image": row.get("Image-URL-M", None),
                "score": float(score),
            }
        )
    return recs


def render_book_card(book_row, show_button=True, key_prefix="top"):
    """Render a single book card (image, title, author, votes, rating)."""
    # book_row is a Series from popular_df
    title = book_row["Book-Title"]
    author = book_row.get("Book-Author", "")
    image = book_row.get("Image-URL-M", None)
    votes = int(book_row.get("num_ratings", 0))
    rating = float(book_row.get("avg_rating", 0.0))

    st.image(image, width=120) if image else st.write("(no image)")
    st.markdown(f"**{title}**")
    st.caption(f"by {author}")
    st.write(f"Votes - {votes}")
    st.write(f"Rating - {rating:.2f}")

    if show_button:
        if st.button("Recommend", key=f"{key_prefix}_rec_{title}"):
            # set selected book and rerun to show recommendations in top area
            st.session_state.selected_book = title
            st.rerun()


# -------------------
# App layout & CSS
# -------------------
st.set_page_config(page_title="Book Recommender", layout="wide")

# --- Replace your existing topbar markdown with this ---
st.markdown("""
<style>
.topbar {
    background: linear-gradient(90deg, #0fa66b, #0fa66b);
    padding: 8px 20px;
    color: white;
    font-family: 'Arial', sans-serif;
    display: flex;
    align-items: center;
    justify-content: space-between;
}
.brand {
    font-size: 18px;
    font-weight: 700;
}
.search-box {
    display: flex;
    gap: 5px;
}
.stTextInput>div>div>input {
    border-radius: 4px;
}
</style>
<div class="topbar">
    <div class="brand">📚 My Book Recommender</div>
    <div class="search-box">
        <!-- Streamlit will render the search input here -->
    </div>
</div>
""", unsafe_allow_html=True)



# -------------------
# Session state
# -------------------
if "selected_book" not in st.session_state:
    st.session_state.selected_book = None

# -------------------
# Search & Recommendation area (top)
# -------------------
top_container = st.container()
with top_container:
    st.markdown("## Find recommendations")
    c1, c2, c3 = st.columns([6, 1, 1])
    with c1:
        # prefill input with selected book if present
        default_val = st.session_state.selected_book or ""
        user_input = st.text_input("Enter a book title or pick one below:", value=default_val, key="search_input")
    with c2:
        if st.button("Recommend", key="search_btn"):
            if user_input and user_input.strip():
                st.session_state.selected_book = user_input.strip()
            else:
                st.warning("Please type a book title or click a Top 50 book.")
    def clear_search():
        st.session_state.search_input = ""
        st.session_state.selected_book = None

    # Inside your layout:
    with c3:
        st.button("Clear", key="clear_btn", on_click=clear_search)

 
    # show recommendations if a book is selected
    if st.session_state.selected_book:
        selected = st.session_state.selected_book
        recs = recommend(selected, n=5)
        st.markdown(f"### Recommendations for: **{selected}**")
        if not recs:
            st.info("No matches found — try a different title or choose from Top 50 below.")
        else:
            cols = st.columns(5)
            for i, book in enumerate(recs):
                with cols[i % 5]:
                    if book["image"]:
                        st.image(book["image"], width=140)
                    st.markdown(f"**{book['title']}**")
                    st.caption(f"by {book['author']}")
    else:
        st.info("Search a book or click 'Show Similar' on any Top 50 book below to see similar reads here.")

st.write("---")



# -------------------
# Top 50 Grid with Perfect Alignment
# -------------------
st.markdown("## 📈 Top 50 Books")
grid_container = st.container()

# Style for fixed-height cards
card_style = """
    <style>
        .book-card {
            border: 1px solid #eee;
            border-radius: 10px;
            padding: 10px;
            text-align: center;
            background: #fff;
            margin-bottom: 15px;
            height: 320px; /* Fixed height for alignment */
            display: flex;
            flex-direction: column;
            justify-content: space-between;
        }
        .book-card img {
            width: 120px;
            height: 160px;
            object-fit: cover;
            border-radius: 5px;
            margin: 0 auto;
        }
        .book-title {
            font-weight: bold;
            margin: 8px 0 4px 0;
            font-size: 14px;
            height: 36px; /* Fix title height */
            overflow: hidden;
        }
        .book-author {
            color: gray;
            font-size: 12px;
            margin: 0;
        }
        .rating {
            margin: 4px 0;
            font-size: 13px;
        }
    </style>
"""
st.markdown(card_style, unsafe_allow_html=True)

cols = st.columns(5)
for idx, row in popular_df.reset_index(drop=True).iterrows():
    col = cols[idx % 5]
    with col:
        st.markdown(
            f"""
            <div class="book-card">
                <div>
                    <img src="{row['Image-URL-M']}">
                    <div class="book-title">{row['Book-Title']}</div>
                    <div class="book-author">by {row['Book-Author']}</div>
                    <div class="rating">⭐ {round(row['avg_rating'],2)} | {row['num_ratings']} votes</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Show Similar", key=f"top_rec_{idx}"):
            st.session_state.selected_book = row['Book-Title']
            st.rerun()


# -------------------
# Show recommendations if book clicked
# -------------------
if "book" in st.query_params:
    st.subheader(f"📚 Recommendations for: {st.query_params['book']}")
    recs = recommend(st.query_params['book'])
    for book in recs:
        st.write(f"✅ {book}")
