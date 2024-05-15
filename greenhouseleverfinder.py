import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit
import urllib.parse
import pandas as pd
import re
import time
import math

def doGoogleSearch(query, numResults, timePeriod, start=0):
    # Construct the search URL
    searchQuery = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={searchQuery}&num={numResults}&start={start}&tbs=qdr:{timePeriod}"
    
    # Set headers to mimic a browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # Make the request to Google
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve results: {response.status_code}")

    # Parse the HTML content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # Extract search result URLs
    searchResults = []
    for g in soup.find_all('div', class_='g'):
        anchor = g.find('a')
        if anchor:
            link = anchor['href']
            searchResults.append(cleanURL(link))
   
    return searchResults

def cleanURL(job_url):

    if "lever.co" in job_url:
        # Split the path after the netloc to preserve the base URL
        pathParts = job_url.split('/')
        pathParts[4] = pathParts[4][:36] # clean up the job number
        if len(pathParts) > 4:
            cleaned_path = '/'.join(pathParts[:5])  # Limit to the first 5 parts
        else:
            cleaned_path = '/'.join(pathParts)
        
        cleaned_url = f"{cleaned_path}"
    
    elif "greenhouse.io" in job_url:
        # Cut off at the first non-numeric character after "jobs/"
        pathParts = job_url.split("/")
        if len(pathParts) > 5:
            # Ensure the 6th item is numeric
            numeric_sixth_item = ''.join([char for char in pathParts[5] if char.isnumeric()])
            # Concatenate the first 6 items
            cleaned_path = '/'.join(pathParts[:5] + [numeric_sixth_item])
            cleaned_url = f"{cleaned_path}" 
        else:
            cleaned_url = job_url
    else:
        cleaned_url = job_url
    
    return cleaned_url

def getJobInfo(url):
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        jobDetails = {
            'companyName': 'N/A',
            'jobRole': 'N/A',
            'location': 'N/A',
            'url': url
        }

        if 'greenhouse' in url:
            # Update extraction logic based on the new HTML structure
            tempCompanyName = soup.find('span', class_='company-name').text.strip() if soup.find('span', class_='company-name') else jobDetails['companyName']
            jobDetails['companyName'] = tempCompanyName[3:]
            jobDetails['jobRole'] = soup.find('h1', class_='app-title').text.strip() if soup.find('h1', class_='app-title') else jobDetails['jobRole']
            jobDetails['location'] = soup.find('div', class_='location').text.strip() if soup.find('div', class_='location') else jobDetails['location']

            if jobDetails['companyName'] == "" or jobDetails['companyName'] == "N/A": 
                pathParts = url.split('/')
                jobDetails['companyName'] = pathParts[3]

        elif 'lever' in url:
            # Extract company name and role title from the title tag
            titleTag = soup.find('title').text if soup.find('title') else ''
            if titleTag:
                parts = titleTag.split(' - ')
                
                jobDetails['companyName'] = parts[0].strip()
                jobDetails['jobRole'] = parts[1].strip()

                if jobDetails['companyName'] == "" or jobDetails['companyName'] == "N/A": 
                    pathParts = url.split('/')
                    jobDetails['companyName'] = pathParts[3]
            
            # Extract location from the div with class including "location"
            location_tag = soup.find('div', class_='posting-categories')
            if location_tag:
                location_div = location_tag.find('div', class_='location')
                if location_div:
                    jobDetails['location'] = location_div.text.strip()
        
        return jobDetails
    else:
        # print(f"Failed to retrieve the job page for URL: {url}")
        return None

def inUSA(location):
    keywords = ['alabama', 'al', 'kentucky', 'ky', 'ohio', 'oh', 'alaska', 'ak', 'louisiana', 'la', 'oklahoma', 'ok', 'arizona', 'az', 'maine', 'me', 'oregon', 'or', 'arkansas', 'ar', 'maryland', 'md', 'pennsylvania', 'pa', 'american samoa', 'as', 'massachusetts', 'ma', 'puerto rico', 'pr', 'california', 'ca', 'michigan', 'mi', 'rhode island', 'ri', 'colorado', 'co', 'minnesota', 'mn', 'south carolina', 'sc', 'connecticut', 'ct', 'mississippi', 'ms', 'south dakota', 'sd', 'delaware', 'de', 'missouri', 'mo', 'tennessee', 'tn', 'district of columbia', 'dc', 'montana', 'mt', 'texas', 'tx', 'florida', 'fl', 'nebraska', 'ne', 'trust territories', 'tt', 'georgia', 'ga', 'nevada', 'nv', 'utah', 'ut', 'guam', 'gu', 'new hampshire', 'nh', 'vermont', 'vt', 'hawaii', 'hi', 'new jersey', 'nj', 'virginia', 'va', 'idaho', 'id', 'new mexico', 'nm', 'virgin islands', 'vi', 'illinois', 'il', 'new york', 'ny', 'washington', 'wa', 'indiana', 'in', 'north carolina', 'nc', 'west virginia', 'wv', 'iowa', 'ia', 'north dakota', 'nd', 'wisconsin', 'wi', 'kansas', 'ks', 'northern mariana islands', 'mp', 'wyoming', 'wy', 'usa', 'united states', 'united', 'states', 'us', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis', 'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville', 'detroit', 'oklahoma city', 'portland', 'las vegas', 'memphis', 'louisville', 'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'kansas city', 'atlanta', 'long beach', 'omaha', 'raleigh', 'colorado springs', 'miami', 'virginia beach', 'oakland', 'minneapolis', 'tulsa', 'arlington', 'tampa', 'new orleans', 'wichita', 'cleveland', 'bakersfield', 'aurora', 'anaheim', 'honolulu', 'santa ana', 'riverside', 'corpus christi', 'lexington', 'stockton', 'henderson', 'saint paul', 'st. louis', 'cincinnati', 'pittsburgh', 'greensboro', 'anchorage', 'plano', 'lincoln', 'orlando', 'irvine', 'newark', 'toledo', 'durham', 'chula vista', 'fort wayne', 'jersey city', 'st. petersburg', 'laredo', 'madison', 'chandler', 'buffalo', 'lubbock', 'scottsdale', 'reno', 'glendale', 'gilbert', 'winston–salem', 'north las vegas', 'norfolk', 'chesapeake', 'garland', 'irving', 'hialeah', 'fremont', 'boise', 'richmond', 'baton rouge', 'spokane', 'des moines', 'tacoma', 'san bernardino', 'modesto', 'fontana', 'santa clarita', 'birmingham', 'oxnard', 'fayetteville', 'moreno valley', 'rochester', 'glendale', 'huntington beach', 'salt lake city', 'grand rapids', 'amarillo', 'yonkers', 'aurora', 'montgomery', 'akron', 'little rock', 'huntsville', 'augusta', 'port st. lucie', 'grand prairie', 'columbus', 'tallahassee', 'overland park', 'tempe', 'mckinney', 'mobile', 'cape coral', 'shreveport', 'frisco', 'knoxville', 'worcester', 'brownsville', 'vancouver', 'fort lauderdale', 'sioux falls', 'ontario', 'chattanooga', 'providence', 'newport news', 'rancho cucamonga', 'santa rosa', 'oceanside', 'salem', 'elk grove', 'garden grove', 'pembroke pines', 'peoria', 'eugene', 'corona', 'cary', 'springfield', 'fort collins', 'jackson', 'alexandria', 'hayward', 'lancaster', 'lakewood', 'clarksville', 'palmdale', 'salinas', 'springfield', 'hollywood', 'pasadena', 'sunnyvale', 'macon', 'pomona', 'escondido', 'killeen', 'naperville', 'joliet', 'bellevue', 'rockford', 'savannah', 'paterson', 'torrance', 'bridgeport', 'mcallen', 'mesquite', 'syracuse', 'midland', 'pasadena', 'murfreesboro', 'miramar', 'dayton', 'fullerton', 'olathe', 'orange', 'thornton', 'roseville', 'denton', 'waco', 'surprise', 'carrollton', 'west valley city', 'charleston', 'warren', 'hampton', 'gainesville', 'visalia', 'coral springs', 'columbia', 'cedar rapids', 'sterling heights', 'new haven', 'stamford', 'concord', 'kent', 'santa clara', 'elizabeth', 'round rock', 'thousand oaks', 'lafayette', 'athens', 'topeka', 'simi valley', 'fargo', 'norman', 'columbia', 'abilene', 'wilmington', 'hartford', 'victorville', 'pearland', 'vallejo', 'ann arbor', 'berkeley', 'allentown', 'richardson', 'odessa', 'arvada', 'cambridge', 'sugar land', 'beaumont', 'lansing', 'evansville', 'rochester', 'independence', 'fairfield', 'provo', 'clearwater', 'college station', 'west jordan', 'carlsbad', 'el monte', 'murrieta', 'temecula', 'springfield', 'palm bay', 'costa mesa', 'westminster', 'north charleston', 'miami gardens', 'manchester', 'high point', 'downey', 'clovis', 'pompano beach', 'pueblo', 'elgin', 'lowell', 'antioch', 'west palm beach', 'peoria', 'everett', 'wilmington', 'ventura', 'centennial', 'lakeland', 'gresham', 'richmond', 'billings', 'inglewood', 'broken arrow', 'sandy springs', 'jurupa valley', 'hillsboro', 'waterbury', 'santa maria', 'boulder', 'greeley', 'daly city', 'meridian', 'lewisville', 'davie', 'west covina', 'league city', 'tyler', 'norwalk', 'san mateo', 'green bay', 'wichita falls', 'sparks', 'lakewood', 'burbank', 'rialto', 'allen', 'el cajon', 'las cruces', 'renton', 'davenport', 'south bend', 'vista', 'tuscaloosa', 'clinton', 'edison', 'woodbridge', 'san angelo', 'kenosha', 'vacaville', 'south gate', 'roswell', 'new bedford', 'yuma', 'longmont', 'brockton', 'quincy', 'sandy', 'waukegan', 'gulfport', 'hesperia', 'bossier city', 'suffolk', 'rochester hills', 'bellingham', 'gary', 'arlington heights', 'livonia', 'tracy', 'edinburg', 'kirkland', 'trenton', 'medford', 'milpitas', 'mission viejo', 'blaine', 'newton', 'upland', 'chino', 'san leandro', 'reading', 'norwalk', 'lynn', 'dearborn', 'new rochelle', 'plantation', 'baldwin park', 'scranton', 'eagan', 'lynnwood', 'utica', 'redwood city', 'dothan', 'carmel', 'merced', 'brooklyn park', 'tamarac', 'burnsville', 'charleston', 'alafaya', 'tustin', 'mount vernon', 'meriden', 'baytown', 'taylorsville', 'turlock', 'apple valley', 'fountain valley', 'leesburg', 'longview', 'bristol', 'valdosta', 'champaign', 'new braunfels', 'san marcos', 'flagstaff', 'manteca', 'santa barbara', 'kennewick', 'roswell', 'harlingen', 'caldwell', 'long beach', 'dearborn', 'murray', 'bryan', 'gainesville', 'lauderhill', 'madison', 'albany', 'joplin', 'missoula', 'iowa city', 'johnson city', 'rapid city', 'sugar land', 'oshkosh', 'mountain view', 'cranston', 'bossier city', 'lawrence', 'bismarck', 'anderson', 'bristol', 'bellingham', 'gulfport', 'dothan', 'farmington', 'redding', 'bryan', 'riverton', 'folsom', 'rock hill', 'new britain', 'carmel', 'temple', 'coral gables', 'concord', 'santa monica', 'wichita falls', 'sioux city', 'hesperia', 'warwick', 'boynton beach', 'troy', 'rosemead', 'missouri city', 'jonesboro', 'perris', 'apple valley', 'hemet', 'whittier', 'carson', 'milpitas', 'midland', 'eastvale', 'upland', 'bolingbrook', 'highlands ranch', 'st. cloud', 'west allis', 'rockville', 'cape coral', 'bowie', 'dubuque', 'broomfield', 'germantown', 'west sacramento', 'north little rock', 'pinellas park', 'casper', 'lancaster', 'gilroy', 'san ramon', 'new rochelle', 'kokomo', 'southfield', 'indian trail', 'cuyahoga falls', 'alameda', 'fort smith', 'kettering', 'carlsbad', 'cedar park', 'twin falls', 'portsmouth', 'sanford', 'chino hills', 'wheaton', 'largo', 'sarasota', 'aliso viejo', 'port orange', 'oak lawn', 'chapel hill', 'redmond', 'milford', 'apopka', 'avondale', 'plainfield', 'auburn', 'doral', 'bozeman', 'jupiter', 'west haven', 'hoboken', 'hoffman estates', 'eagan', 'blaine', 'apex', 'tinley park', 'palo alto', 'orland park', "coeur d'alene", 'burleson', 'casa grande', 'pittsfield', 'decatur', 'la habra', 'dublin', 'marysville', 'north port', 'valdosta', 'twin falls', 'blacksburg', 'perris', 'caldwell', 'largo', 'bartlett', 'middletown', 'decatur', 'warwick', 'conroe', 'waterloo', 'oakland park', 'bartlesville', 'wausau', 'harrisonburg', 'farmington hills', 'la crosse', 'enid', 'pico rivera', 'newark', 'palm coast', 'wellington', 'calexico', 'lancaster', 'north miami', 'riverton', 'blacksburg', 'goodyear', 'roseville', 'homestead', 'hoffman estates', 'montebello', 'casa grande', 'morgan hill', 'milford', 'murray', 'jackson', 'blaine', 'port arthur', 'kearny', 'bullhead city', 'castle rock', 'st. cloud', 'grand island', 'rockwall', 'westfield', 'little elm', 'la puente', 'lehi', 'diamond bar', 'keller', 'harrisonburg', 'saginaw', 'sammamish', 'kendall', 'georgetown', 'owensboro', 'trenton', 'keller', 'findlay', 'lakewood', 'leander', 'rocklin', 'san clemente', 'sheboygan', 'kennewick', 'draper', 'menifee', 'cuyahoga falls', 'johnson city', 'manhattan', 'rowlett', 'san bruno', 'coon rapids', 'murray', 'revere', 'sheboygan', 'east orange', 'south jordan', 'highland', 'la quinta', 'alamogordo', 'madison', 'broomfield', 'beaumont', 'newark', 'weston', 'peabody', 'union city', 'coachella', 'palatine', 'montebello', 'taylorsville', 'twin falls', 'east lansing', 'alamogordo', 'la mesa', 'blaine', 'pittsburg', 'caldwell', 'hoboken', 'huntersville', 'south whittier', 'redlands', 'janesville', 'beverly', 'burien', 'owensboro', 'wheaton', 'redmond', 'glenview', 'leominster', 'bountiful', 'oak creek', 'florissant', 'commerce city', 'pflugerville', 'westfield', 'auburn', 'shawnee', 'san rafael', 'alamogordo', 'murray', 'brentwood', 'revere', 'pflugerville', 'aliso viejo', 'auburn', 'florissant', 'national city', 'la mesa', 'leominster', 'pico rivera', 'castle rock', 'springfield']
    
    if location == 'N/A': 
        return True
        
    delimiters = [",", "/", "-","(", ")"]
    pattern = '|'.join(map(re.escape, delimiters))
    words = re.split(pattern, location)
    for word in words:
        if word.lower() in keywords:
            return True
    return False

def isRelevantRole(jobRole):
    if jobRole == 'N/A': 
        return True
    
    keywords = ["computer", "vision", "perception", "software", "machine", "learning", 
                "artificial", "intelligence", "nlp", "natural", "language", "processing", 
                "llm", "cv", "development", "ai", "ml", "sde", "swe", "backend",
                "frontend", "fullstack", "full", "stack", "architect", "researcher",
                 "engineer", "scientist", "devops", "mlops", "cloud", "system", "systems"]
    ignore = ["staff", "sr.", "sr", "senior", "manager", "lead", "principal", "director", "sales",
              "head", "mechanical", "ii", "iii", "iv", "l2", "l3", "management", "consultant", "phd"]

    delimiters = [",", "/", "-","(", ")", " "]
    pattern = '|'.join(map(re.escape, delimiters))
    words = re.split(pattern, jobRole)
    isMatchingWord = False
    for word in words:
        if word.lower() in ignore: 
            return False
        else: 
            if word.lower() in keywords:
                isMatchingWord = True
    return isMatchingWord

def saveToExcel(data, filename):
    df = pd.DataFrame(data)
    df.to_excel(filename, index=False)

query = "(intitle:engineer OR intitle:scientist OR intitle:researcher OR intitle:architect) site:lever.co OR site:greenhouse.io -intitle:staff -intitle:senior -intitle:manager -intitle:lead -intitle:principal -intitle:director"

numResults = input("Enter the number of results: ")
timePeriod = input("How recent should the results be: ")

resultsPerPage = 100  # As google generally returns atmost 100 results at a time

urls = []

# if max, then stop fetching jobs when under 100 are returned
if numResults == "max": 
    i = 0
    while True:
        results = doGoogleSearch(query, resultsPerPage, timePeriod, i*resultsPerPage)
        urls.extend(results)
        print(f"Fetched {len(results)} results starting from {i*resultsPerPage}")
        time.sleep(2) # get by google rate limit
        if len(results) < resultsPerPage: 
            break
        i+=1

# if number given, continue fetching till number reached
else: 
    remaining = int(numResults)
    for start in range(math.ceil(int(numResults)/resultsPerPage)):
        resultsToReturn = min(remaining,resultsPerPage)
        results = doGoogleSearch(query, resultsToReturn, timePeriod, start*resultsPerPage)
        urls.extend(results)
        print(f"Fetched {len(results)} results starting from {start*resultsPerPage}")
        remaining -= resultsToReturn
        time.sleep(2) # get by google rate limit

jobList = []
jobListNoDetails = []

for url in urls:
    jobInfo = getJobInfo(url)
    if jobInfo:
        if inUSA(jobInfo['location']) and isRelevantRole(jobInfo['jobRole']):
            if jobInfo['jobRole'] != "N/A": 
                jobList.append(jobInfo)   
            else: 
                jobListNoDetails.append(jobInfo)

print(len(jobList), " relevant jobs found!")
print(len(jobListNoDetails), " relevant (maybe) jobs found!")

saveToExcel(jobList, 'jobs.xlsx')
saveToExcel(jobListNoDetails, 'jobsNoDetails.xlsx')
print("Job listings to jobs.xlsx and jobsNoDetails.xlsx")
