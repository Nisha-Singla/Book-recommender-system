# Book Recommender System

This project is a Book Recommender System built with Python. It uses collaborative filtering and popularity-based algorithms to suggest books to users based on their preferences and ratings.

## Features
- Recommends books based on user ratings and similarity scores
- Displays popular books
- Uses preprocessed datasets for efficient recommendations
- Interactive interface (likely via Streamlit or Jupyter Notebook)

## Project Structure
- `app.py`: Main application script
- `book_recommender_system.ipynb`: Jupyter notebook for exploration and prototyping
- `requirements.txt`: List of required Python packages
- `artifacts/`: Contains preprocessed data files (`books.pkl`, `popular.pkl`, `similarity_scores.pkl`)
- `data/`: Raw datasets (`Books.csv`, `Ratings.csv`, `Users.csv`, `pt.pkl`)

## How It Works
1. Loads book, user, and rating data
2. Processes data to compute popularity and similarity scores
3. Provides recommendations based on user input

## Getting Started
1. Install dependencies:
   ```powershell
   pip install -r requirements.txt
   ```
2. Run the application:
   ```powershell
   streamlit run app.py
   ```
   Or open `book_recommender_system.ipynb` in Jupyter Notebook for interactive exploration.

## Requirements
- Python 3.10+
- See `requirements.txt` for all dependencies

## Data Sources
- `Books.csv`, `Ratings.csv`, `Users.csv`: Raw data for recommendations

## Author
- Nisha Singla

## License
This project is for educational purposes.
