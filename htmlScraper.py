import requests
from bs4 import BeautifulSoup

# URL of the page you want to scrape
url = 'https://www.google.com/search?q=(engineer+OR+software)+(machine+learning+OR+%22software+engineer%22+OR+%22software+develop%22+OR+%22natural+language+processing%22+OR+%22computer+vision%22+OR+%22perception%22)+site:lever.co+OR+site:greenhouse.io+location:US+-staff+-senior+-principal+-manager+-lead&sca_esv=a0ffaebd0ed0b666&source=lnt&tbs=qdr:w&sa=X&ved=2ahUKEwiPjPaImf2FAxW1LFkFHd4ODgwQpwV6BAgCEAk&biw=1862&bih=894&dpr=1.38#ip=1'

# Send a GET request
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    print(soup.prettify())  # This will print the nicely formatted HTML
else:
    print("Failed to retrieve the page")

