import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit, parse_qs, urlunsplit
from googlesearch import search
import urllib.parse
import pandas as pd



def get_google_search_results(query, num_results=5, time='h'):
    # Construct the search URL
    search_query = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={search_query}&num={num_results}&tbs=qdr:{time}"
    
    # Set headers to mimic a browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make the request to Google
    response = requests.get(url, headers=headers)
    
    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract search result URLs
    search_results = []
    for g in soup.find_all('div', class_='g'):
        anchor = g.find('a')
        if anchor:
            link = anchor['href']
            # Filter URLs containing "jobs"
            # if "jobs" in link.lower():
            search_results.append(link)
            # print(f"URL: {link}")
    
    return search_results
 
def get_job_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        job_details = {
            'company_name': 'N/A',
            'role_title': 'N/A',
            'location': 'N/A',
            'url': url
        }
        if 'greenhouse' in url:
            # Update extraction logic based on the new HTML structure
            temp_company_name = soup.find('span', class_='company-name').text.strip() if soup.find('span', class_='company-name') else job_details['company_name']
            job_details['company_name'] = temp_company_name[3:]
            job_details['role_title'] = soup.find('h1', class_='app-title').text.strip() if soup.find('h1', class_='app-title') else job_details['role_title']
            job_details['location'] = soup.find('div', class_='location').text.strip() if soup.find('div', class_='location') else job_details['location']
        
        elif 'lever' in url:
            job_details['company_name'] = soup.find('div', class_='posting-headline').find('h2').text.strip() if soup.find('div', class_='posting-headline') and soup.find('div', class_='posting-headline').find('h2') else job_details['company_name']
            job_details['role_title'] = soup.find('h2', class_='posting-title').text.strip() if soup.find('h2', class_='posting-title') else job_details['role_title']
            location_tag = soup.find('div', class_='posting-categories')
            if location_tag:
                job_details['location'] = location_tag.find('a').text.strip() if location_tag.find('a') else job_details['location']
        return job_details
    else:
        print(f"Failed to retrieve the job page for URL: {url}")
        return None

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

# Example usage
query = "(engineer OR software) (machine learning OR software engineer OR software develop OR natural language processing OR computer vision OR perception) site:lever.co OR site:greenhouse.io location:US -staff -senior -Sr. -principal -manager -lead"
num_results = input("Enter the number of results: ")
time_range = input("How recent should the results be: ")
urls = get_google_search_results(query,num_results,time_range)

job_list = []
for url in urls:
    job_info = get_job_details(url)
    if job_info:
        job_list.append(job_info)

save_to_excel(job_list, 'job_listings.xlsx')
print("Job listings saved to job_listings.xlsx")
    

# def clean_url(url):
#     # Parse the query parameters
#     query = urlsplit(url).query
#     parsed_query = parse_qs(query)
    
#     # Extract the actual job link from the 'q' parameter
#     if 'q' in parsed_query:
#         job_url = parsed_query['q'][0]
#     else:
#         return url  # Return the original URL if 'q' is not present

#     if "lever.co" in job_url:
#         # Split the path after the netloc to preserve the base URL
#         path_parts = job_url.split('/')
#         if len(path_parts) > 4:
#             cleaned_path = '/'.join(path_parts[:5])  # Limit to the first 5 parts
#         else:
#             cleaned_path = '/'.join(path_parts)
        
#         # Construct the cleaned URL
#         netloc = urlsplit(job_url).netloc
#         cleaned_url = f"{cleaned_path}"
    
#     elif "greenhouse.io" in job_url:
#         # Cut off at the first non-numeric character after "jobs/"
#         path_parts = job_url.split("/")
#         if len(path_parts) > 5:
#             # Ensure the 6th item is numeric
#             numeric_sixth_item = ''.join([char for char in path_parts[5] if char.isnumeric()])
#             # Concatenate the first 6 items
#             cleaned_path = '/'.join(path_parts[:5] + [numeric_sixth_item])
#             cleaned_url = f"{cleaned_path}"
#         else:
#             cleaned_url = job_url
#     else:
#         cleaned_url = job_url
    
#     return cleaned_url

# # URL of the page you want to scrape
# url = 'https://www.google.com/search?q=(engineer+OR+software)+(machine+learning+OR+%22software+engineer%22+OR+%22software+develop%22+OR+%22natural+language+processing%22+OR+%22computer+vision%22+OR+%22perception%22)+site%3Alever.co+OR+site%3Agreenhouse.io+location%3AUS+-staff+-senior+-principal+-manager+-lead&oq=(engineer+OR+software)+(machine+learning+OR+%22software+engineer%22+OR+%22software+develop%22+OR+%22natural+language+processing%22+OR+%22computer+vision%22+OR+%22perception%22)+site%3Alever.co+OR+site%3Agreenhouse.io+location%3AUS+-staff+-senior+-principal+-manager+-lead&gs_lcrp=EgZjaHJvbWUyBggAEEUYOTIGCAEQRRg7MgYIAhBFGDvSAQgzODIzajBqN6gCALACAA&sourceid=chrome&ie=UTF-8#ip=1'

# # Send a GET request
# response = requests.get(url)

# # Ensure the request was successful
# if response.status_code == 200:
#     html_content = response.text
#     # Parse the HTML content using Beautiful Soup
#     soup = BeautifulSoup(html_content, 'html.parser')
    
#     # Find all <a> tags with URLs pointing to job postings
#     job_links = soup.find_all('a', href=True)
    
#     # Filter out links and print them
#     for link in job_links:
#         href = link['href']
#         if "https://boards.greenhouse.io" in href or "https://jobs.lever.co" in href:
#             cleaned_href = clean_url(href)
#             print(cleaned_href)
# else:
#     print("Failed to retrieve the page")

# job_urls = [
#     'https://boards.greenhouse.io/waymo/jobs/5853040 '
#     'https://boards.greenhouse.io/waymo/jobs/5853062'
#     'https://boards.greenhouse.io/waymo/jobs/5896019'
#     'https://boards.greenhouse.io/grammarly/jobs/5932771'
#     'https://boards.greenhouse.io/vannevarlabs/jobs/4366534007'
#     'https://boards.greenhouse.io/offerfit/jobs/4416058005'
#     'https://boards.greenhouse.io/pinterestjobadvertisements/jobs/5951216'
#     'https://boards.greenhouse.io/d2l/jobs/5947933'
#     'https://jobs.lever.co/whoop/faeef488-7276-47f8-81d9-7087c252345c/apply'
#     'https://boards.greenhouse.io/technergetics/jobs/4361465006'
# ]

# # Fetch and print job details for each URL
