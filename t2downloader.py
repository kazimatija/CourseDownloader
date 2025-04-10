import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, unquote  # unquote to decode URL-encoded characters

# Start a session to handle login
session = requests.Session()

# The URL where the login form is posted (from the HTML form's action attribute)
base_url = 'https://lists.etf.bg.ac.rs/wws/'

# Your login credentials
email = '...'
password = '...'

# Set up the login data
data = {
    'email': email,
    'passwd': password,
    'action': 'login',
    'action_login': 'Login',
    'previous_action': '',
    'previous_list': '',
    'referer': '',
    'list': ''
}

# Set a user-agent to simulate a browser request
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
}

# Perform the login by posting the data
response = session.post(base_url, data=data, headers=headers)

# Check if the login was successful
if response.ok:
    print('Logged in successfully!')
else:
    print('Failed to log in. Status code:', response.status_code)

# The URL of the page with the list of PDF links
url = 'https://lists.etf.bg.ac.rs/wws/d_read/13e033t2/Dodatni%20materijali%20-%202024/'

# The folder to save the PDFs
save_folder = r'...'

# Function to download PDF from a given URL
def download_pdf(pdf_url, save_folder):
    # Set headers for the download request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': url  # Ensure the referer is set correctly
    }

    response = session.get(pdf_url, headers=headers)

    # Debugging: Check the response headers and content type
    print(f"Downloading: {pdf_url}")
    print(f"Response status code: {response.status_code}")
    print(f"Content-Type: {response.headers.get('Content-Type')}")

    # If the request is successful (status code 200), save the file
    if response.status_code == 200:
        # Check if the content is a PDF based on the Content-Type header
        if 'pdf' in response.headers.get('Content-Type', '').lower():
            # Decode the filename (remove %20 and other URL encodings)
            filename = unquote(pdf_url.split('/')[-1])
            file_path = os.path.join(save_folder, filename)
            
            # Save the PDF content to the file
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print(f"Downloaded: {filename}")
        else:
            print(f"Error: The file at {pdf_url} is not a PDF.")
    else:
        print(f"Failed to download: {pdf_url}, Status code: {response.status_code}")

# Function to extract PDF links from the webpage
def extract_pdf_links(page_url):
    response = session.get(page_url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Find all anchor tags and filter those that link to PDFs
        links = soup.find_all('a', href=True)
        pdf_links = []

        for link in links:
            href = link['href']
            # Check if the link ends with '.pdf' or if it's a relative URL
            if href.endswith('.pdf'):
                pdf_links.append(urljoin(page_url, href))  # Resolve relative URL properly
            elif href.startswith('/') and '.pdf' in href:
                # Handling relative paths
                pdf_links.append(urljoin(base_url, href))
                
        return pdf_links
    else:
        print("Failed to retrieve the webpage.")
        return []

# Main execution
def main():
    # Ensure the save folder exists
    os.makedirs(save_folder, exist_ok=True)

    # Extract PDF links
    pdf_links = extract_pdf_links(url)
    
    if pdf_links:
        print(f"Found {len(pdf_links)} PDF links.")
        for pdf_url in pdf_links:
            print(f"Attempting to download: {pdf_url}")
            download_pdf(pdf_url, save_folder)
    else:
        print("No PDF links found.")

# Run the script
if __name__ == "__main__":
    main()
