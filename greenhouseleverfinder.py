import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import urllib.parse
import pandas as pd
import re

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

            search_results.append(clean_url(link))
            # print(f"URL: {link}")
    
    return search_results

def clean_url(job_url):

    if "lever.co" in job_url:
        # Split the path after the netloc to preserve the base URL
        path_parts = job_url.split('/')
        if len(path_parts) > 4:
            cleaned_path = '/'.join(path_parts[:5])  # Limit to the first 5 parts
        else:
            cleaned_path = '/'.join(path_parts)
        
        # Construct the cleaned URL
        netloc = urlsplit(job_url).netloc
        cleaned_url = f"{cleaned_path}"
    
    elif "greenhouse.io" in job_url:
        # Cut off at the first non-numeric character after "jobs/"
        path_parts = job_url.split("/")
        if len(path_parts) > 5:
            # Ensure the 6th item is numeric
            numeric_sixth_item = ''.join([char for char in path_parts[5] if char.isnumeric()])
            # Concatenate the first 6 items
            cleaned_path = '/'.join(path_parts[:5] + [numeric_sixth_item])
            cleaned_url = f"{cleaned_path}"
        else:
            cleaned_url = job_url
    else:
        cleaned_url = job_url
    
    return cleaned_url

def get_job_details(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        job_details = {
            'company_name': 'N/A',
            'role_title': 'N/A',
            'location': 'N/A',
            'in_us': 'N/A',
            'url': url
        }

        if 'greenhouse' in url:
            # Update extraction logic based on the new HTML structure
            temp_company_name = soup.find('span', class_='company-name').text.strip() if soup.find('span', class_='company-name') else job_details['company_name']
            job_details['company_name'] = temp_company_name[3:]
            job_details['role_title'] = soup.find('h1', class_='app-title').text.strip() if soup.find('h1', class_='app-title') else job_details['role_title']
            job_details['location'] = soup.find('div', class_='location').text.strip() if soup.find('div', class_='location') else job_details['location']
        
        elif 'lever' in url:
            # Extract company name and role title from the title tag
            title_tag = soup.find('title').text if soup.find('title') else ''
            if title_tag:
                parts = title_tag.split(' - ')
                if len(parts) == 2:
                    job_details['company_name'] = parts[0].strip()
                    job_details['role_title'] = parts[1].strip()
            
            # Extract location from the div with class including "location"
            location_tag = soup.find('div', class_='posting-categories')
            if location_tag:
                location_div = location_tag.find('div', class_='location')
                if location_div:
                    job_details['location'] = location_div.text.strip()
        
        return job_details
    else:
        print(f"Failed to retrieve the job page for URL: {url}")
        return None

def is_us_location(location):
    keywords = ['alabama', 'al', 'kentucky', 'ky', 'ohio', 'oh', 'alaska', 'ak', 'louisiana', 'la', 'oklahoma', 'ok', 'arizona', 'az', 'maine', 'me', 'oregon', 'or', 'arkansas', 'ar', 'maryland', 'md', 'pennsylvania', 'pa', 'american samoa', 'as', 'massachusetts', 'ma', 'puerto rico', 'pr', 'california', 'ca', 'michigan', 'mi', 'rhode island', 'ri', 'colorado', 'co', 'minnesota', 'mn', 'south carolina', 'sc', 'connecticut', 'ct', 'mississippi', 'ms', 'south dakota', 'sd', 'delaware', 'de', 'missouri', 'mo', 'tennessee', 'tn', 'district of columbia', 'dc', 'montana', 'mt', 'texas', 'tx', 'florida', 'fl', 'nebraska', 'ne', 'trust territories', 'tt', 'georgia', 'ga', 'nevada', 'nv', 'utah', 'ut', 'guam', 'gu', 'new hampshire', 'nh', 'vermont', 'vt', 'hawaii', 'hi', 'new jersey', 'nj', 'virginia', 'va', 'idaho', 'id', 'new mexico', 'nm', 'virgin islands', 'vi', 'illinois', 'il', 'new york', 'ny', 'washington', 'wa', 'indiana', 'in', 'north carolina', 'nc', 'west virginia', 'wv', 'iowa', 'ia', 'north dakota', 'nd', 'wisconsin', 'wi', 'kansas', 'ks', 'northern mariana islands', 'mp', 'wyoming', 'wy', 'usa', 'united states', 'us', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis', 'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville', 'detroit', 'oklahoma city', 'portland', 'las vegas', 'memphis', 'louisville', 'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'kansas city', 'atlanta', 'long beach', 'omaha', 'raleigh', 'colorado springs', 'miami', 'virginia beach', 'oakland', 'minneapolis', 'tulsa', 'arlington', 'tampa', 'new orleans', 'wichita', 'cleveland', 'bakersfield', 'aurora', 'anaheim', 'honolulu', 'santa ana', 'riverside', 'corpus christi', 'lexington', 'stockton', 'henderson', 'saint paul', 'st. louis', 'cincinnati', 'pittsburgh', 'greensboro', 'anchorage', 'plano', 'lincoln', 'orlando', 'irvine', 'newark', 'toledo', 'durham', 'chula vista', 'fort wayne', 'jersey city', 'st. petersburg', 'laredo', 'madison', 'chandler', 'buffalo', 'lubbock', 'scottsdale', 'reno', 'glendale', 'gilbert', 'winston–salem', 'north las vegas', 'norfolk', 'chesapeake', 'garland', 'irving', 'hialeah', 'fremont', 'boise', 'richmond', 'baton rouge', 'spokane', 'des moines', 'tacoma', 'san bernardino', 'modesto', 'fontana', 'santa clarita', 'birmingham', 'oxnard', 'fayetteville', 'moreno valley', 'rochester', 'glendale', 'huntington beach', 'salt lake city', 'grand rapids', 'amarillo', 'yonkers', 'aurora', 'montgomery', 'akron', 'little rock', 'huntsville', 'augusta', 'port st. lucie', 'grand prairie', 'columbus', 'tallahassee', 'overland park', 'tempe', 'mckinney', 'mobile', 'cape coral', 'shreveport', 'frisco', 'knoxville', 'worcester', 'brownsville', 'vancouver', 'fort lauderdale', 'sioux falls', 'ontario', 'chattanooga', 'providence', 'newport news', 'rancho cucamonga', 'santa rosa', 'oceanside', 'salem', 'elk grove', 'garden grove', 'pembroke pines', 'peoria', 'eugene', 'corona', 'cary', 'springfield', 'fort collins', 'jackson', 'alexandria', 'hayward', 'lancaster', 'lakewood', 'clarksville', 'palmdale', 'salinas', 'springfield', 'hollywood', 'pasadena', 'sunnyvale', 'macon', 'pomona', 'escondido', 'killeen', 'naperville', 'joliet', 'bellevue', 'rockford', 'savannah', 'paterson', 'torrance', 'bridgeport', 'mcallen', 'mesquite', 'syracuse', 'midland', 'pasadena', 'murfreesboro', 'miramar', 'dayton', 'fullerton', 'olathe', 'orange', 'thornton', 'roseville', 'denton', 'waco', 'surprise', 'carrollton', 'west valley city', 'charleston', 'warren', 'hampton', 'gainesville', 'visalia', 'coral springs', 'columbia', 'cedar rapids', 'sterling heights', 'new haven', 'stamford', 'concord', 'kent', 'santa clara', 'elizabeth', 'round rock', 'thousand oaks', 'lafayette', 'athens', 'topeka', 'simi valley', 'fargo', 'norman', 'columbia', 'abilene', 'wilmington', 'hartford', 'victorville', 'pearland', 'vallejo', 'ann arbor', 'berkeley', 'allentown', 'richardson', 'odessa', 'arvada', 'cambridge', 'sugar land', 'beaumont', 'lansing', 'evansville', 'rochester', 'independence', 'fairfield', 'provo', 'clearwater', 'college station', 'west jordan', 'carlsbad', 'el monte', 'murrieta', 'temecula', 'springfield', 'palm bay', 'costa mesa', 'westminster', 'north charleston', 'miami gardens', 'manchester', 'high point', 'downey', 'clovis', 'pompano beach', 'pueblo', 'elgin', 'lowell', 'antioch', 'west palm beach', 'peoria', 'everett', 'wilmington', 'ventura', 'centennial', 'lakeland', 'gresham', 'richmond', 'billings', 'inglewood', 'broken arrow', 'sandy springs', 'jurupa valley', 'hillsboro', 'waterbury', 'santa maria', 'boulder', 'greeley', 'daly city', 'meridian', 'lewisville', 'davie', 'west covina', 'league city', 'tyler', 'norwalk', 'san mateo', 'green bay', 'wichita falls', 'sparks', 'lakewood', 'burbank', 'rialto', 'allen', 'el cajon', 'las cruces', 'renton', 'davenport', 'south bend', 'vista', 'tuscaloosa', 'clinton', 'edison', 'woodbridge', 'san angelo', 'kenosha', 'vacaville', 'south gate', 'roswell', 'new bedford', 'yuma', 'longmont', 'brockton', 'quincy', 'sandy', 'waukegan', 'gulfport', 'hesperia', 'bossier city', 'suffolk', 'rochester hills', 'bellingham', 'gary', 'arlington heights', 'livonia', 'tracy', 'edinburg', 'kirkland', 'trenton', 'medford', 'milpitas', 'mission viejo', 'blaine', 'newton', 'upland', 'chino', 'san leandro', 'reading', 'norwalk', 'lynn', 'dearborn', 'new rochelle', 'plantation', 'baldwin park', 'scranton', 'eagan', 'lynnwood', 'utica', 'redwood city', 'dothan', 'carmel', 'merced', 'brooklyn park', 'tamarac', 'burnsville', 'charleston', 'alafaya', 'tustin', 'mount vernon', 'meriden', 'baytown', 'taylorsville', 'turlock', 'apple valley', 'fountain valley', 'leesburg', 'longview', 'bristol', 'valdosta', 'champaign', 'new braunfels', 'san marcos', 'flagstaff', 'manteca', 'santa barbara', 'kennewick', 'roswell', 'harlingen', 'caldwell', 'long beach', 'dearborn', 'murray', 'bryan', 'gainesville', 'lauderhill', 'madison', 'albany', 'joplin', 'missoula', 'iowa city', 'johnson city', 'rapid city', 'sugar land', 'oshkosh', 'mountain view', 'cranston', 'bossier city', 'lawrence', 'bismarck', 'anderson', 'bristol', 'bellingham', 'gulfport', 'dothan', 'farmington', 'redding', 'bryan', 'riverton', 'folsom', 'rock hill', 'new britain', 'carmel', 'temple', 'coral gables', 'concord', 'santa monica', 'wichita falls', 'sioux city', 'hesperia', 'warwick', 'boynton beach', 'troy', 'rosemead', 'missouri city', 'jonesboro', 'perris', 'apple valley', 'hemet', 'whittier', 'carson', 'milpitas', 'midland', 'eastvale', 'upland', 'bolingbrook', 'highlands ranch', 'st. cloud', 'west allis', 'rockville', 'cape coral', 'bowie', 'dubuque', 'broomfield', 'germantown', 'west sacramento', 'north little rock', 'pinellas park', 'casper', 'lancaster', 'gilroy', 'san ramon', 'new rochelle', 'kokomo', 'southfield', 'indian trail', 'cuyahoga falls', 'alameda', 'fort smith', 'kettering', 'carlsbad', 'cedar park', 'twin falls', 'portsmouth', 'sanford', 'chino hills', 'wheaton', 'largo', 'sarasota', 'aliso viejo', 'port orange', 'oak lawn', 'chapel hill', 'redmond', 'milford', 'apopka', 'avondale', 'plainfield', 'auburn', 'doral', 'bozeman', 'jupiter', 'west haven', 'hoboken', 'hoffman estates', 'eagan', 'blaine', 'apex', 'tinley park', 'palo alto', 'orland park', "coeur d'alene", 'burleson', 'casa grande', 'pittsfield', 'decatur', 'la habra', 'dublin', 'marysville', 'north port', 'valdosta', 'twin falls', 'blacksburg', 'perris', 'caldwell', 'largo', 'bartlett', 'middletown', 'decatur', 'warwick', 'conroe', 'waterloo', 'oakland park', 'bartlesville', 'wausau', 'harrisonburg', 'farmington hills', 'la crosse', 'enid', 'pico rivera', 'newark', 'palm coast', 'wellington', 'calexico', 'lancaster', 'north miami', 'riverton', 'blacksburg', 'goodyear', 'roseville', 'homestead', 'hoffman estates', 'montebello', 'casa grande', 'morgan hill', 'milford', 'murray', 'jackson', 'blaine', 'port arthur', 'kearny', 'bullhead city', 'castle rock', 'st. cloud', 'grand island', 'rockwall', 'westfield', 'little elm', 'la puente', 'lehi', 'diamond bar', 'keller', 'harrisonburg', 'saginaw', 'sammamish', 'kendall', 'georgetown', 'owensboro', 'trenton', 'keller', 'findlay', 'lakewood', 'leander', 'rocklin', 'san clemente', 'sheboygan', 'kennewick', 'draper', 'menifee', 'cuyahoga falls', 'johnson city', 'manhattan', 'rowlett', 'san bruno', 'coon rapids', 'murray', 'revere', 'sheboygan', 'east orange', 'south jordan', 'highland', 'la quinta', 'alamogordo', 'madison', 'broomfield', 'beaumont', 'newark', 'weston', 'peabody', 'union city', 'coachella', 'palatine', 'montebello', 'taylorsville', 'twin falls', 'east lansing', 'alamogordo', 'la mesa', 'blaine', 'pittsburg', 'caldwell', 'hoboken', 'huntersville', 'south whittier', 'redlands', 'janesville', 'beverly', 'burien', 'owensboro', 'wheaton', 'redmond', 'glenview', 'leominster', 'bountiful', 'oak creek', 'florissant', 'commerce city', 'pflugerville', 'westfield', 'auburn', 'shawnee', 'san rafael', 'alamogordo', 'murray', 'brentwood', 'revere', 'pflugerville', 'aliso viejo', 'auburn', 'florissant', 'national city', 'la mesa', 'leominster', 'pico rivera', 'castle rock', 'springfield']
    
    if location == 'N/A': 
        return True
    
    delimiters = [",", "/", "-"]
    pattern = '|'.join(map(re.escape, delimiters))
    words = re.split(pattern, location)

    for word in words:
        if word.lower() in keywords:
            return True
    return False

def save_to_excel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

query = "site:lever.co OR site:greenhouse.io location:US -staff -senior -Sr. -principal -manager -lead"
num_results = input("Enter the number of results: ")
time_range = input("How recent should the results be: ")
urls = get_google_search_results(query,num_results,time_range)

job_list = []
for url in urls:
    job_info = get_job_details(url)
    if job_info:
        job_info['in_us'] = is_us_location(job_info['location'])
        job_list.append(job_info)

save_to_excel(job_list, 'job_listings.xlsx')
print("Job listings saved to job_listings.xlsx")

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
