

import streamlit as st
import pickle
import numpy as np
from difflib import get_close_matches

# -------------------
# Load data with error handling
# -------------------
try:
    # Load data files from their respective directories
    pt = pickle.load(open("data/pt.pkl", "rb"))                    # pivot table index = Book-Title
    books = pickle.load(open("artifacts/books.pkl", "rb"))        # full books dataframe
    similarity_scores = pickle.load(open("artifacts/similarity_scores.pkl", "rb"))
    popular_df = pickle.load(open("artifacts/popular.pkl", "rb"))  # top 50 popular books (num_ratings, avg_rating, etc)
    st.success("✅ All data files loaded successfully!")
except FileNotFoundError as e:
    st.error(f"❌ Data file not found: {e}")
    st.error("Please make sure all required files are in the correct directories:")
    st.error("- data/pt.pkl")
    st.error("- artifacts/books.pkl")
    st.error("- artifacts/similarity_scores.pkl")
    st.error("- artifacts/popular.pkl")
    st.stop()
except Exception as e:
    st.error(f"❌ Error loading data files: {e}")
    st.stop()

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
        try:
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
        except (IndexError, KeyError) as e:
            # Skip this book if there's an error
            continue
    return recs


# -------------------
# App layout & CSS
# -------------------
st.set_page_config(page_title="Book Recommender", layout="wide")

# --- Improved topbar styling with better alignment ---
st.markdown("""
<style>
.topbar {
    background: linear-gradient(90deg, #0fa66b, #0fa66b);
    padding: 12px 30px;
    color: white;
    font-family: 'Arial', sans-serif;
    display: flex;
    align-items: center;
    justify-content: space-between;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    position: sticky;
    top: 0;
    z-index: 100;
}
.brand {
    font-size: 20px;
    font-weight: 700;
    display: flex;
    align-items: center;
    gap: 8px;
}
.search-container {
    display: flex;
    align-items: center;
    gap: 10px;
    flex: 1;
    max-width: 500px;
    margin: 0 20px;
}
.stTextInput > div > div > input {
    border-radius: 6px;
    border: none;
    padding: 8px 12px;
    font-size: 14px;
    height: 40px;
}
.stButton > button {
    border-radius: 6px;
    padding: 8px 16px;
    font-weight: 500;
    border: none;
    cursor: pointer;
    transition: all 0.2s ease;
}
.stButton > button:hover {
    opacity: 0.9;
    transform: translateY(-1px);
}
.clear-btn {
    background: rgba(255,255,255,0.2) !important;
    color: white !important;
    border: 1px solid rgba(255,255,255,0.3) !important;
}
.clear-btn:hover {
    background: rgba(255,255,255,0.3) !important;
}
</style>
""", unsafe_allow_html=True)

# Render the actual topbar
st.markdown("""
<div class="topbar">
    <div class="brand">📚 My Book Recommender</div>
    <div class="search-container">
        <!-- Search input will be rendered here -->
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
                st.rerun()
            else:
                st.warning("Please type a book title or click a Top 50 book.")
    def clear_search():
        st.session_state.search_input = ""
        st.session_state.selected_book = None
        st.rerun()

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

# Style for improved book cards with better alignment and responsive design
card_style = """
    <style>
        .book-card {
            border: 1px solid #e0e0e0;
            border-radius: 12px;
            padding: 12px;
            text-align: center;
            background: #fff;
            margin-bottom: 20px;
            height: 340px;
            display: flex;
            flex-direction: column;
            justify-content: space-between;
            box-shadow: 0 2px 8px rgba(0,0,0,0.1);
            transition: all 0.3s ease;
            position: relative;
            overflow: hidden;
        }
        .book-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 16px rgba(0,0,0,0.15);
        }
        .book-card img {
            width: 130px;
            height: 180px;
            object-fit: cover;
            border-radius: 8px;
            margin: 0 auto 8px auto;
            border: 2px solid #f0f0f0;
        }
        .book-title {
            font-weight: 600;
            margin: 6px 0 4px 0;
            font-size: 13px;
            line-height: 1.3;
            height: 42px;
            overflow: hidden;
            display: -webkit-box;
            -webkit-line-clamp: 3;
            -webkit-box-orient: vertical;
            color: #333;
        }
        .book-author {
            color: #666;
            font-size: 11px;
            margin: 0 0 6px 0;
            font-style: italic;
        }
        .rating {
            margin: 4px 0;
            font-size: 12px;
            color: #0fa66b;
            font-weight: 500;
        }
        .book-card .stButton {
            margin-top: 8px;
        }
        .book-card .stButton > button {
            background: linear-gradient(90deg, #0fa66b, #0fa66b);
            color: white;
            border: none;
            border-radius: 6px;
            padding: 6px 12px;
            font-size: 11px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s ease;
            width: 100%;
        }
        .book-card .stButton > button:hover {
            opacity: 0.9;
            transform: translateY(-1px);
        }
        @media (max-width: 768px) {
            .book-card {
                height: 320px;
                padding: 8px;
            }
            .book-card img {
                width: 110px;
                height: 150px;
            }
            .book-title {
                font-size: 12px;
                height: 36px;
            }
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
                <div class="card-content">
                    <img src="{row['Image-URL-M']}" alt="{row['Book-Title']}" onerror="this.src='https://via.placeholder.com/130x180?text=No+Image'">
                    <div class="book-title">{row['Book-Title']}</div>
                    <div class="book-author">by {row['Book-Author']}</div>
                    <div class="rating">⭐ {round(row['avg_rating'],2)} | {row['num_ratings']} votes</div>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if st.button("Show Similar", key=f"top_rec_{idx}", help=f"Show similar books to {row['Book-Title']}"):
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
