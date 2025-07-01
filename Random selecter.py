import pandas as pd
import random

# Corrected file path
df = pd.read_csv(r'c:\Users\harri\AppData\Local\Temp\c3af1121-2117-4442-b511-afbbe70cdbbe_ml-latest-small.zip.ml-latest-small.zip\ml-latest-small\movies.csv')

def random_movies_by_genre(genre, n=5):
    filtered = df[df['genres'].str.contains(genre, case=False, na=False)]
    return filtered.sample(n=min(n, len(filtered)))[['title', 'genres']]

# Example usage:
print(random_movies_by_genre('Comedy', 5))