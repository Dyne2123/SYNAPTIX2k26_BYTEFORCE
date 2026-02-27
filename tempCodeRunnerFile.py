
from openlibrary import OpenLibrary

def recommend_books(interest, n=5):
    ol = OpenLibrary()
    
    # Search for books based on interest
    results = ol.search(interest)
    
    if not results:
        return f"No books found for '{interest}'"
    
    recommendations = []
    for book in results[:n]:
        title = book.title
        authors = ", ".join([a['name'] for a in book.authors]) if book.authors else "Unknown"
        link = f"https://openlibrary.org{book.key}"
        recommendations.append(f"📖 {title}\n👤 {authors}\n🔗 {link}")
    
    return recommendations

# Example usage
interest = "Artificial Intelligence"
books = recommend_books(interest)

print("\n".join(books))