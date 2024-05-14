import requests
from bs4 import BeautifulSoup
import sys

# Function to get the title, author, and description of the article
def get_article_details(url):
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        soup = BeautifulSoup(response.content, 'html.parser')

        # Get the title
        title = None
        if soup.find('title'):
            title = soup.find('title').text
        elif soup.find('meta', attrs={'property': 'og:title'}):
            title = soup.find('meta', attrs={'property': 'og:title'})['content']
        elif soup.find('meta', attrs={'name': 'title'}):
            title = soup.find('meta', attrs={'name': 'title'})['content']
        else:
            title = 'No Title'

        # Convert title to title case
        title = title.title()

        # Get the description
        description = None
        if soup.find('meta', attrs={'name': 'description'}):
            description = soup.find('meta', attrs={'name': 'description'})['content']
        elif soup.find('meta', attrs={'property': 'og:description'}):
            description = soup.find('meta', attrs={'property': 'og:description'})['content']
        elif soup.find('meta', attrs={'name': 'twitter:description'}):
            description = soup.find('meta', attrs={'name': 'twitter:description'})['content']
        else:
            paragraphs = soup.find_all('p')
            if paragraphs:
                description = ' '.join([para.text for para in paragraphs[:3]])
            else:
                description = 'No Description'

        # Get the author
        author = 'Unknown Author'
        if soup.find('meta', attrs={'name': 'author'}):
            author = soup.find('meta', attrs={'name': 'author'})['content']
        elif soup.find('meta', attrs={'property': 'article:author'}):
            author = soup.find('meta', attrs={'property': 'article:author'})['content']
        elif soup.find('meta', attrs={'name': 'byline'}):
            author = soup.find('meta', attrs={'name': 'byline'})['content']

        # Format author line
        author_line = f"By {author}" if author != 'Unknown Author' else "By Unknown Author"

        return title.strip(), author_line, description.strip()

    except requests.RequestException as e:
        print(f"Error fetching details for {url}: {e}")
        return 'No Title', 'By Unknown Author', 'No Description'

# Function to read URLs from a file
def read_urls_from_file(filename):
    with open(filename, 'r') as file:
        urls = file.readlines()
    # Remove any whitespace characters like `\n` at the end of each line
    urls = [url.strip() for url in urls]
    return urls

# Function to write article details to a file
def write_articles_to_file(urls, output_filename):
    with open(output_filename, 'w') as file:
        for url in urls:
            title, author, description = get_article_details(url)
            file.write("---\n")
            file.write(f"{title}\n")
            file.write(f"{author}\n")
            file.write(f"\"{description}\"\n")
            file.write(f"{url}\n")

# Check if input filename is provided
if len(sys.argv) < 2:
    print("Usage: python url_to_summary.py <input_filename>")
    sys.exit(1)

# Input and output filenames
input_filename = sys.argv[1]
output_filename = 'articles.txt'

# Read URLs from the input file
urls = read_urls_from_file(input_filename)

# Write article details to the output file
write_articles_to_file(urls, output_filename)

print(f"Article details have been written to {output_filename}")
