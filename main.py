import openai
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import base64

# Load environment variables
load_dotenv()

# OpenAI API
openai.api_key = os.getenv("OPENAI_API_KEY")

# WordPress API
wp_url = os.getenv("WP_URL")
wp_username = os.getenv("WP_USERNAME")

# WP Application Password
app_password = os.getenv("WP_APP_PASSWORD")
credentials = wp_username + ':' + app_password
token = base64.b64encode(credentials.encode())


# Define a list of books
def get_nyt_best_nonfiction(num_books=1):
    books = []
    page_num = 1
    while len(books) < num_books:
        # Make a GET request to the Goodreads page with the page number
        page = requests.get("https://www.goodreads.com/list/show/11306.New_York_Times_Best_Nonfiction_Books",
                            params={"page": page_num})

        # Parse the HTML of the page
        soup = BeautifulSoup(page.content, 'html.parser')

        # Find the table containing the list of books
        table = soup.find(id='all_votes')

        # Iterate over the rows of the table
        for row in table.find_all('tr'):
            # Get the columns of the row
            cols = row.find_all('td')

            # Extract the information for the book
            title = cols[2].find('a', class_='bookTitle').text.strip()
            author = cols[2].find('a', class_='authorName').text.strip()

            # Get the URL of the book's page on Goodreads
            book_title_link = cols[2].find('a', class_='bookTitle')
            if book_title_link:
                book_url = book_title_link['href']

            # Make a GET request to the book's page on Goodreads
            book_page = requests.get(f"https://www.goodreads.com{book_title_link['href']}")

            # Parse the HTML of the book's page
            book_soup = BeautifulSoup(book_page.content, 'html.parser')

            # Find the image of the book's cover
            book_cover_container = book_soup.find(class_='bookCoverContainer')
            if book_cover_container:
                image = book_cover_container['style']

            # Extract the URL of the image
            image_url = image.split('url(')[1].split(')')[0]

            # Download the image
            image_data = requests.get(image_url).content

            # Save the image to a file
            with open("image.jpg", "wb") as f:
                f.write(image_data)

            # Read the image file
            with open("image.jpg", "rb") as f:
                image_file = f.read()

            # Add the book to the list
            books.append({'title': title, 'author': author, 'image': image_file})

        # Increment the page number
        page_num += 1

        # Break out of the loop if there are no more pages
        if not soup.find("a", {"class": "next_page"}):
            break

    return books[:num_books]


books = get_nyt_best_nonfiction()

for book in books:
    print(f"{book['title']} by {book['author']}")


# Generate a book report using ChatGPT for each book and store it in a list
def generate_book_report(book):
    # Define the prompt for the GPT-3 model
    prompt = f"Generate a book report for {book['title']} by {book['author']}"

    # Send a request to the GPT-3 API and get the response
    response = openai.Completion.create(engine="text-davinci-002", prompt=prompt, max_tokens=1024)

    # Print the generated text
    return (response["choices"][0]["text"])


books = get_nyt_best_nonfiction()

book_reports = []

for book in books:
    book_report = generate_book_report(book)
    book_reports.append(book_report)


# Post the generated book report to WordPress
def post_book_report(book_report):
    # Set the headers for the API request
    headers = {
        'Authorization': 'Basic ' + token.decode('utf-8')
    }

    # Set the data for the API request
    data = {
        "title": book['title'] + ' by ' + book['author'],
        "content": book_report,
        "status": "publish",
        "categories": [3],
        "comment_status": "closed"
    }

    files = {
        "featured_image": book['cover']
    }

    # Send a POST request to the WordPress API to create a new post
    response = requests.post(wp_url, headers=headers, data=data, files=files)

    # Print the response from the API
    print(response.text)


books = get_nyt_best_nonfiction()

for book in books:
    book_report = generate_book_report(book)
    post_book_report(book_report)
