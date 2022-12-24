import openai
import requests
from bs4 import BeautifulSoup
from requests.structures import CaseInsensitiveDict

# Set up OpenAI API client
openai.api_key = "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"

# Set up WordPress API client
wp_url = "http://steveshickles.com/wp-json/wp/v2/posts"
wp_username = "shickles"
wp_password = "mdc3cuj2nrw7MQE.rhg"

# Define a list of books
def get_nyt_best_nonfiction(num_books=3):

    # Make a GET request to the Goodreads page
    page = requests.get("https://www.goodreads.com/list/show/11306.New_York_Times_Best_Nonfiction_Books")

    # Parse the HTML of the page
    soup = BeautifulSoup(page.content, 'html.parser')

    # Find the table containing the list of books
    table = soup.find(id='all_votes')

    # Initialize an empty list to store the books
    books = []

    # Iterate over the rows of the table
    for row in table.find_all('tr'):
        # Get the columns of the row
        cols = row.find_all('td')

        # Extract the information for the book
        title = cols[2].find('a', class_='bookTitle').text.strip()
        author = cols[2].find('a', class_='authorName').text.strip()

        # Add the book to the list
        books.append({  'title': title, 'author': author})

    return books

# Create a function that generates a book report using ChatGPT
def generate_book_report(title, author):
  # Use ChatGPT to generate a book report
  response = openai.Completion.create(
    model="text-davinci-002",
    prompt=f"Write a book report for the book '{title}' by {author}.",
    max_tokens=1024
  )
  report = response['choices'][0]['text']
  return report

# Create a function that posts a book report to WordPress
def post_book_report(title, author, report):
  # Set up HTTP headers
  headers = CaseInsensitiveDict()
  headers["Content-Type"] = "application/json"
  # Set up authentication
  auth = (wp_username, wp_password)
  # Set up payload
  payload = {
    "title": title,
    "author": author,
    "content": report,
    "status": "publish"
  }
  # Make HTTP POST request to WordPress API
  response = requests.post(wp_url, json=payload, headers=headers, auth=auth)
  # Check if request was successful
  if response.status_code == 201:
    print(f"Successfully posted book report for '{title}' to WordPress!")
  else:
    print(f"Error posting book report for '{title}' to WordPress: {response.status_code}")




# Iterate over the list of books and generate a report for each one
for book in get_nyt_best_nonfiction():
  title = book['title']
  author = book['author']
  report = generate_book_report(title, author)
  post_book_report(title, author, report)


