import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, urlunsplit

def clean_url(url):
    # Split the URL into components
    split_url = urlsplit(url)
    # Reconstruct the URL without the query and fragment components
    cleaned_url = urlunsplit((split_url.scheme, split_url.netloc, split_url.path, '', ''))
    return cleaned_url

def get_job_details(url):
    # Clean the URL to avoid tracking parameters and other unnecessary parts
    url = clean_url(url)
    
    # Send a GET request to the job listing page
    response = requests.get(url)
    
    # Check if the request was successful
    if response.status_code == 200:
        # Parse the HTML content
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract details based on common class names or ids from Greenhouse and Lever
        job_details = {
            'company_name': 'N/A',
            'role_title': 'N/A',
            'location': 'N/A',
            'date_posted': 'N/A'
        }
        
        # Different extraction logic based on platform
        if 'greenhouse' in url:
            job_details['company_name'] = soup.find('div', class_='level-0').text.strip() if soup.find('div', class_='level-0') else job_details['company_name']
            job_details['role_title'] = soup.find('h1').text.strip() if soup.find('h1') else job_details['role_title']
            job_details['location'] = soup.find('div', class_='location').text.strip() if soup.find('div', class_='location') else job_details['location']
            job_details['date_posted'] = soup.find('span', class_='posted-date').text.strip() if soup.find('span', class_='posted-date') else job_details['date_posted']
        
        elif 'lever' in url:
            job_details['company_name'] = soup.find('div', class_='posting-headline').find('h2').text.strip() if soup.find('div', class_='posting-headline') and soup.find('div', class_='posting-headline').find('h2') else job_details['company_name']
            job_details['role_title'] = soup.find('h2', class_='posting-title').text.strip() if soup.find('h2', class_='posting-title') else job_details['role_title']
            # Lever pages often include the location next to the role title
            location_tag = soup.find('div', class_='posting-categories')
            if location_tag:
                job_details['location'] = location_tag.find('a').text.strip() if location_tag.find('a') else job_details['location']
        
        return job_details
    else:
        print(f"Failed to retrieve the job page for URL: {url}")
        return None
    
# URL of the page you want to scrape
url = 'https://www.google.com/search?q=(engineer+OR+software)+(machine+learning+OR+%22software+engineer%22+OR+%22software+develop%22+OR+%22natural+language+processing%22+OR+%22computer+vision%22+OR+%22perception%22)+site:lever.co+OR+site:greenhouse.io+location:US+-staff+-senior+-principal+-manager+-lead&sca_esv=a0ffaebd0ed0b666&source=lnt&tbs=qdr:w&sa=X&ved=2ahUKEwiPjPaImf2FAxW1LFkFHd4ODgwQpwV6BAgCEAk&biw=1862&bih=894&dpr=1.38#ip=1'

# Send a GET request
response = requests.get(url)

# Ensure the request was successful
if response.status_code == 200:
    html_content = response.text
    # Parse the HTML content using Beautiful Soup
    soup = BeautifulSoup(html_content, 'html.parser')
    
    # Find all <a> tags with URLs pointing to job postings
    job_links = soup.find_all('a', href=True)
    
    # Filter out links and print them
    for link in job_links:
        href = link['href']
        if "https://boards.greenhouse.io" in href or "https://jobs.lever.co" in href:
            print("Job Link: \n", href[7:])
else:
    print("Failed to retrieve the page")

job_urls = [
    'https://boards.greenhouse.io/waymo/jobs/5896019&sa=U&ved=2ahUKEwjGl7nsnv2FAxV8jIkEHd5vB-oQFnoECAYQAg&usg=AOvVaw0PVRfJLO3tM7qVA4PkmJoZ',
    'https://jobs.lever.co/whoop/faeef488-7276-47f8-81d9-7087c252345c/apply&sa=U&ved=2ahUKEwjGl7nsnv2FAxV8jIkEHd5vB-oQFnoECAQQAg&usg=AOvVaw0RSY9XWQcVQaYgTg5l8753',
    # More URLs can be added here
]

# Fetch and print job details for each URL
for job_url in job_urls:
    job_info = get_job_details(job_url)
    if job_info:
        print(job_info)