import requests
from bs4 import BeautifulSoup
import urllib.parse
import pandas as pd
import re
import time
import math
import xlsxwriter
from datetime import datetime

keywordsDict = {
    'sde' : ["software development", "software engineer", "software engineering", 
             "software developer", "development", "backend engineer", "sde", "swe", "backend", 
             "frontend", "fullstack", "full", "stack", "front", "system", "systems",
             "cloud", "devops", "application", "api", "platform", "site"],

    'aiml' : ["machine learning", "artificial intelligence", "ai", "ml", "mlops",
            "cloud", "devops", "generative", "deep", "data", "applied"],

    'cv' : ["computer vision", "computer", "vision", "perception", "cv", "image", "object", "detection",
            "autonomous"],

    'nlp' : ["nlp", "natural language processing", "llm", "generative", "linguist", 
            "language", "applied"],                  
    
    'robo' : ["robotics", "robot", "mechatronics", "automation", "autonomous"],
}

ignoreDict = {
    'title' : ["staff", "sr.", "sr", "senior", "manager", "lead", "chief", "principal", "director",
              "sales", "head", "mechanical", "ii", "iii", "iv", "l2", "l3", "2", "3", "4", 
              "management", "consultant", "phd", "manufacturing", "law", "maintenance", 
              "construction", "clearance", "structures", "helpdesk", "electrical", "propulsion",
              "solution", "solutions", "customer"],
    'description' : ["clearance", "itar"]
}

# determine which roles to add to the list based on user input
def selectRoles(whichRoles):
    keywords = []
    if whichRoles == 'all':
        for role in keywordsDict: 
            keywords.extend(keywordsDict[role])
    else:
        # split input by comma, add to list
        inputRoles = whichRoles.split(',')
        for role in inputRoles:
            role = role.strip()  # Clean up whitespace
            if role in keywordsDict:
                keywords.extend(keywordsDict[role])
            else:
                print(f"Unsupported role: {role}")
    return keywords

# perform a google search on the query provided
def doGoogleSearch(query, numResults, timePeriod, start):   

    # construct search query
    searchQuery = urllib.parse.quote_plus(query)
    url = f"https://www.google.com/search?q={searchQuery}&num={numResults}&start={start}&tbs=qdr:{timePeriod}"
    
    # headers to mimic browser visit
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    # google request
    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        print(f"Failed to retrieve results: {response.status_code}")

    # parse html content
    soup = BeautifulSoup(response.text, "html.parser")
    
    # extract urls
    searchResults = []
    for g in soup.find_all('div', class_='g'):
        anchor = g.find('a')
        if anchor:
            link = anchor['href']
            searchResults.append(cleanURL(link))
   
    return searchResults

# remove irrelevant portions of the urls
def cleanURL(job_url):
    if "lever.co" in job_url:

        # split url, remove all characters after the job id
        pathParts = job_url.split('/')
        pathParts[4] = pathParts[4][:36] 

        # if more than 4 parts, keep only the first 5
        if len(pathParts) > 4:
            cleaned_path = '/'.join(pathParts[:5])  
        else:
            cleaned_path = '/'.join(pathParts)
        
        cleaned_url = f"{cleaned_path}"
    
    elif "greenhouse.io" in job_url:
        
        # cut off at the first non numeric character after "jobs/"
        pathParts = job_url.split("/")
        if len(pathParts) > 5:
        
            # ensure the 6th item is numeric, then add to rest of the url
            numeric_sixth_item = ''.join([char for char in pathParts[5] if char.isnumeric()])
            cleaned_path = '/'.join(pathParts[:5] + [numeric_sixth_item])
            cleaned_url = f"{cleaned_path}" 
        else:
            cleaned_url = job_url
    else:
        cleaned_url = job_url
    
    return cleaned_url

# retreive job title, company name, location from the pages html
def getJobInfo(url):
    try:
        response = requests.get(url)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            jobDetails = {
                'Company Name': 'N/A',
                'Job Title': 'N/A',
                'Location': 'N/A',
                'Job Description': 'N/A',  
                'url': url
            }

            if 'greenhouse' in url:
                jobDetails['Company Name'] = (soup.find('span', class_='company-name').text.strip() 
                                              if soup.find('span', class_='company-name') else 'N/A')[3:]
                jobDetails['Job Title'] = (soup.find('h1', class_='app-title').text.strip() 
                                           if soup.find('h1', class_='app-title') else 'N/A')
                jobDetails['Location'] = (soup.find('div', class_='location').text.strip() 
                                          if soup.find('div', class_='location') else 'N/A')
                jobDescription_tag = soup.find('div', id='content')
                jobDetails['Job Description'] = jobDescription_tag.text.strip() if jobDescription_tag else 'N/A'

            elif 'lever' in url:
                titleTag = soup.find('title').text if soup.find('title') else ''
                if titleTag:
                    parts = titleTag.split(' - ')
                    if len(parts) >= 2:
                        jobDetails['Company Name'] = parts[0].strip()
                        jobDetails['Job Title'] = parts[1].strip()

                location_tag = soup.find('div', class_='posting-categories')
                if location_tag:
                    location_div = location_tag.find('div', class_='location')
                    jobDetails['Location'] = location_div.text.strip() if location_div else 'N/A'

                jobDescription_tag = soup.find('div', attrs={'data-qa': 'job-description'})
                jobDetails['Job Description'] = jobDescription_tag.text.strip() if jobDescription_tag else 'N/A'

            return jobDetails
        else:
            # print(f"Failed to retrieve page: {response.status_code}")
            return None
    except requests.exceptions.RequestException as e:
        print(f"HTTP request failed: {e}")
        return None

# check if the location is based in the USA
def inUSA(location):
    keywords = ['None', 'remote', 'na', 'silicon valley', 'alabama', 'al', 'kentucky', 'ky', 'ohio', 'oh', 'alaska', 'ak', 'louisiana', 'la', 'oklahoma', 'ok', 'arizona', 'az', 'maine', 'me', 'oregon', 'or', 'arkansas', 'ar', 'maryland', 'md', 'pennsylvania', 'pa', 'american samoa', 'as', 'massachusetts', 'ma', 'puerto rico', 'pr', 'california', 'ca', 'michigan', 'mi', 'rhode island', 'ri', 'colorado', 'co', 'minnesota', 'mn', 'south carolina', 'sc', 'connecticut', 'ct', 'mississippi', 'ms', 'south dakota', 'sd', 'delaware', 'de', 'missouri', 'mo', 'tennessee', 'tn', 'district of columbia', 'dc', 'montana', 'mt', 'texas', 'tx', 'florida', 'fl', 'nebraska', 'ne', 'trust territories', 'tt', 'georgia', 'ga', 'nevada', 'nv', 'utah', 'ut', 'guam', 'gu', 'new hampshire', 'nh', 'vermont', 'vt', 'hawaii', 'hi', 'new jersey', 'nj', 'virginia', 'va', 'idaho', 'id', 'new mexico', 'nm', 'virgin islands', 'vi', 'illinois', 'il', 'new york', 'ny', 'washington', 'wa', 'indiana', 'in', 'north carolina', 'nc', 'west virginia', 'wv', 'iowa', 'ia', 'north dakota', 'nd', 'wisconsin', 'wi', 'kansas', 'ks', 'northern mariana islands', 'mp', 'wyoming', 'wy', 'usa', 'united states', 'united', 'states', 'us', 'new york', 'los angeles', 'chicago', 'houston', 'phoenix', 'philadelphia', 'san antonio', 'san diego', 'dallas', 'san jose', 'austin', 'jacksonville', 'fort worth', 'columbus', 'charlotte', 'san francisco', 'indianapolis', 'seattle', 'denver', 'washington', 'boston', 'el paso', 'nashville', 'detroit', 'oklahoma city', 'portland', 'las vegas', 'memphis', 'louisville', 'baltimore', 'milwaukee', 'albuquerque', 'tucson', 'fresno', 'sacramento', 'mesa', 'kansas city', 'atlanta', 'long beach', 'omaha', 'raleigh', 'colorado springs', 'miami', 'virginia beach', 'oakland', 'minneapolis', 'tulsa', 'arlington', 'tampa', 'new orleans', 'wichita', 'cleveland', 'bakersfield', 'aurora', 'anaheim', 'honolulu', 'santa ana', 'riverside', 'corpus christi', 'lexington', 'stockton', 'henderson', 'saint paul', 'st. louis', 'cincinnati', 'pittsburgh', 'greensboro', 'anchorage', 'plano', 'lincoln', 'orlando', 'irvine', 'newark', 'toledo', 'durham', 'chula vista', 'fort wayne', 'jersey city', 'st. petersburg', 'laredo', 'madison', 'chandler', 'buffalo', 'lubbock', 'scottsdale', 'reno', 'glendale', 'gilbert', 'winston–salem', 'north las vegas', 'norfolk', 'chesapeake', 'garland', 'irving', 'hialeah', 'fremont', 'boise', 'richmond', 'baton rouge', 'spokane', 'des moines', 'tacoma', 'san bernardino', 'modesto', 'fontana', 'santa clarita', 'birmingham', 'oxnard', 'fayetteville', 'moreno valley', 'rochester', 'glendale', 'huntington beach', 'salt lake city', 'grand rapids', 'amarillo', 'yonkers', 'aurora', 'montgomery', 'akron', 'little rock', 'huntsville', 'augusta', 'port st. lucie', 'grand prairie', 'columbus', 'tallahassee', 'overland park', 'tempe', 'mckinney', 'mobile', 'cape coral', 'shreveport', 'frisco', 'knoxville', 'worcester', 'brownsville', 'vancouver', 'fort lauderdale', 'sioux falls', 'ontario', 'chattanooga', 'providence', 'newport news', 'rancho cucamonga', 'santa rosa', 'oceanside', 'salem', 'elk grove', 'garden grove', 'pembroke pines', 'peoria', 'eugene', 'corona', 'cary', 'springfield', 'fort collins', 'jackson', 'alexandria', 'hayward', 'lancaster', 'lakewood', 'clarksville', 'palmdale', 'salinas', 'springfield', 'hollywood', 'pasadena', 'sunnyvale', 'macon', 'pomona', 'escondido', 'killeen', 'naperville', 'joliet', 'bellevue', 'rockford', 'savannah', 'paterson', 'torrance', 'bridgeport', 'mcallen', 'mesquite', 'syracuse', 'midland', 'pasadena', 'murfreesboro', 'miramar', 'dayton', 'fullerton', 'olathe', 'orange', 'thornton', 'roseville', 'denton', 'waco', 'surprise', 'carrollton', 'west valley city', 'charleston', 'warren', 'hampton', 'gainesville', 'visalia', 'coral springs', 'columbia', 'cedar rapids', 'sterling heights', 'new haven', 'stamford', 'concord', 'kent', 'santa clara', 'elizabeth', 'round rock', 'thousand oaks', 'lafayette', 'athens', 'topeka', 'simi valley', 'fargo', 'norman', 'columbia', 'abilene', 'wilmington', 'hartford', 'victorville', 'pearland', 'vallejo', 'ann arbor', 'berkeley', 'allentown', 'richardson', 'odessa', 'arvada', 'cambridge', 'sugar land', 'beaumont', 'lansing', 'evansville', 'rochester', 'independence', 'fairfield', 'provo', 'clearwater', 'college station', 'west jordan', 'carlsbad', 'el monte', 'murrieta', 'temecula', 'springfield', 'palm bay', 'costa mesa', 'westminster', 'north charleston', 'miami gardens', 'manchester', 'high point', 'downey', 'clovis', 'pompano beach', 'pueblo', 'elgin', 'lowell', 'antioch', 'west palm beach', 'peoria', 'everett', 'wilmington', 'ventura', 'centennial', 'lakeland', 'gresham', 'richmond', 'billings', 'inglewood', 'broken arrow', 'sandy springs', 'jurupa valley', 'hillsboro', 'waterbury', 'santa maria', 'boulder', 'greeley', 'daly city', 'meridian', 'lewisville', 'davie', 'west covina', 'league city', 'tyler', 'norwalk', 'san mateo', 'green bay', 'wichita falls', 'sparks', 'lakewood', 'burbank', 'rialto', 'allen', 'el cajon', 'las cruces', 'renton', 'davenport', 'south bend', 'vista', 'tuscaloosa', 'clinton', 'edison', 'woodbridge', 'san angelo', 'kenosha', 'vacaville', 'south gate', 'roswell', 'new bedford', 'yuma', 'longmont', 'brockton', 'quincy', 'sandy', 'waukegan', 'gulfport', 'hesperia', 'bossier city', 'suffolk', 'rochester hills', 'bellingham', 'gary', 'arlington heights', 'livonia', 'tracy', 'edinburg', 'kirkland', 'trenton', 'medford', 'milpitas', 'mission viejo', 'blaine', 'newton', 'upland', 'chino', 'san leandro', 'reading', 'norwalk', 'lynn', 'dearborn', 'new rochelle', 'plantation', 'baldwin park', 'scranton', 'eagan', 'lynnwood', 'utica', 'redwood city', 'dothan', 'carmel', 'merced', 'brooklyn park', 'tamarac', 'burnsville', 'charleston', 'alafaya', 'tustin', 'mount vernon', 'meriden', 'baytown', 'taylorsville', 'turlock', 'apple valley', 'fountain valley', 'leesburg', 'longview', 'bristol', 'valdosta', 'champaign', 'new braunfels', 'san marcos', 'flagstaff', 'manteca', 'santa barbara', 'kennewick', 'roswell', 'harlingen', 'caldwell', 'long beach', 'dearborn', 'murray', 'bryan', 'gainesville', 'lauderhill', 'madison', 'albany', 'joplin', 'missoula', 'iowa city', 'johnson city', 'rapid city', 'sugar land', 'oshkosh', 'mountain view', 'cranston', 'bossier city', 'lawrence', 'bismarck', 'anderson', 'bristol', 'bellingham', 'gulfport', 'dothan', 'farmington', 'redding', 'bryan', 'riverton', 'folsom', 'rock hill', 'new britain', 'carmel', 'temple', 'coral gables', 'concord', 'santa monica', 'wichita falls', 'sioux city', 'hesperia', 'warwick', 'boynton beach', 'troy', 'rosemead', 'missouri city', 'jonesboro', 'perris', 'apple valley', 'hemet', 'whittier', 'carson', 'milpitas', 'midland', 'eastvale', 'upland', 'bolingbrook', 'highlands ranch', 'st. cloud', 'west allis', 'rockville', 'cape coral', 'bowie', 'dubuque', 'broomfield', 'germantown', 'west sacramento', 'north little rock', 'pinellas park', 'casper', 'lancaster', 'gilroy', 'san ramon', 'new rochelle', 'kokomo', 'southfield', 'indian trail', 'cuyahoga falls', 'alameda', 'fort smith', 'kettering', 'carlsbad', 'cedar park', 'twin falls', 'portsmouth', 'sanford', 'chino hills', 'wheaton', 'largo', 'sarasota', 'aliso viejo', 'port orange', 'oak lawn', 'chapel hill', 'redmond', 'milford', 'apopka', 'avondale', 'plainfield', 'auburn', 'doral', 'bozeman', 'jupiter', 'west haven', 'hoboken', 'hoffman estates', 'eagan', 'blaine', 'apex', 'tinley park', 'palo alto', 'orland park', "coeur d'alene", 'burleson', 'casa grande', 'pittsfield', 'decatur', 'la habra', 'dublin', 'marysville', 'north port', 'valdosta', 'twin falls', 'blacksburg', 'perris', 'caldwell', 'largo', 'bartlett', 'middletown', 'decatur', 'warwick', 'conroe', 'waterloo', 'oakland park', 'bartlesville', 'wausau', 'harrisonburg', 'farmington hills', 'la crosse', 'enid', 'pico rivera', 'newark', 'palm coast', 'wellington', 'calexico', 'lancaster', 'north miami', 'riverton', 'blacksburg', 'goodyear', 'roseville', 'homestead', 'hoffman estates', 'montebello', 'casa grande', 'morgan hill', 'milford', 'murray', 'jackson', 'blaine', 'port arthur', 'kearny', 'bullhead city', 'castle rock', 'st. cloud', 'grand island', 'rockwall', 'westfield', 'little elm', 'la puente', 'lehi', 'diamond bar', 'keller', 'harrisonburg', 'saginaw', 'sammamish', 'kendall', 'georgetown', 'owensboro', 'trenton', 'keller', 'findlay', 'lakewood', 'leander', 'rocklin', 'san clemente', 'sheboygan', 'kennewick', 'draper', 'menifee', 'cuyahoga falls', 'johnson city', 'manhattan', 'rowlett', 'san bruno', 'coon rapids', 'murray', 'revere', 'sheboygan', 'east orange', 'south jordan', 'highland', 'la quinta', 'alamogordo', 'madison', 'broomfield', 'beaumont', 'newark', 'weston', 'peabody', 'union city', 'coachella', 'palatine', 'montebello', 'taylorsville', 'twin falls', 'east lansing', 'alamogordo', 'la mesa', 'blaine', 'pittsburg', 'caldwell', 'hoboken', 'huntersville', 'south whittier', 'redlands', 'janesville', 'beverly', 'burien', 'owensboro', 'wheaton', 'redmond', 'glenview', 'leominster', 'bountiful', 'oak creek', 'florissant', 'commerce city', 'pflugerville', 'westfield', 'auburn', 'shawnee', 'san rafael', 'alamogordo', 'murray', 'brentwood', 'revere', 'pflugerville', 'aliso viejo', 'auburn', 'florissant', 'national city', 'la mesa', 'leominster', 'pico rivera', 'castle rock', 'springfield']
    
    if location == 'N/A': 
        return True
        
    # split the location, and check each word to see if its in the keywords
    delimiters = [",", "/", "-","(", ")"]
    pattern = '|'.join(map(re.escape, delimiters))

    words = re.split(pattern, location)
    for word in words:
        if word.lower() in keywords:
            return True
    return False

# check if the role is relevant against selected keywords
def isRelevantRole(jobTitle, jobDescription, keywords):
    if jobTitle == 'N/A' and jobDescription == 'N/A': 
        return True
        
    titleLower = jobTitle.lower()
    descriptionLower = jobDescription.lower()

    # iterate through delimited words in job role and description
    # if job role contains a single "ignore" word, return false
    # if no "ignore" words, and >=1 relevant keywords, return true
    if any(ignored in titleLower for ignored in ignoreDict['title']):
        return False
    if any(ignored in descriptionLower for ignored in ignoreDict['description']):
        return False
    
    return any(keyword.lower() in titleLower for keyword in keywords) or any(keyword.lower() in descriptionLower for keyword in keywords)
    

def saveToExcel(jobList, jobListNoDetails, jobListRejected, timePeriod):
    current_time = datetime.now().strftime("%H-%M, %d-%m-%Y")

    # date and time in filename
    filename = f'/data/jobListings-{timePeriod}-{current_time}.xlsx'

    # create dataframes
    df_jobs = pd.DataFrame(jobList)
    df_jobs_no_details = pd.DataFrame(jobListNoDetails)
    df_jobs_rejected = pd.DataFrame(jobListRejected)


    # write to the same excel file, different sheets
    with pd.ExcelWriter(filename, engine='xlsxwriter') as writer:
        df_jobs.to_excel(writer, sheet_name='Relevant Jobs', index=False)
        df_jobs_no_details.to_excel(writer, sheet_name='Relevant (Maybe) Jobs', index=False)
        df_jobs_rejected.to_excel(writer, sheet_name='Rejected Jobs', index=False)

    print(f"Data saved to {filename}")

# main function
def scrapeJobsMain(): 

    numResults = input("How many results to fetch ('max', or an integer > 0): ")
    if len(numResults) == 0: # default values
        numResults = "max"
        print("Set to default: max")
            
    timePeriod = input("How recent should the results be (h-hour, d-day, w-week, m-month, y-year): ")
    if len(timePeriod) == 0: # default values
        timePeriod = "d"
        print("Set to default: d")

    whichRoles = input("What roles are you interested in (sde, aiml, cv, nlp, robo, all): ")
    if len(whichRoles) == 0: # default values
        whichRoles = "all"
        print("Set to default: all")

    query = "(intitle:engineer OR intitle:scientist OR intitle:researcher OR intitle:architect) site:lever.co OR site:greenhouse.io -intitle:staff -intitle:senior -intitle:manager -intitle:lead -intitle:principal -intitle:director"

    keywords = selectRoles(whichRoles)

    resultsPerPage = 100  # As google generally returns atmost 100 results at a time

    urls = []

    print("Fetching results...")
    # if max, then stop fetching jobs when under 100 are returned
    if numResults == "max": 
        i = 0
        while True:
            results = doGoogleSearch(query, resultsPerPage, timePeriod, i*resultsPerPage)
            urls.extend(results)
            # print(f"Fetched {len(results)} results starting from {i*resultsPerPage}")
            time.sleep(2) # get by google rate limit
            if len(results) < resultsPerPage: 
                break
            i+=1
        print((i*100) + len(results), " results fetched.")

    # if number given, continue fetching till number reached
    else: 
        remaining = int(numResults)
        for start in range(math.ceil(int(numResults)/resultsPerPage)):
            resultsToReturn = min(remaining,resultsPerPage)
            results = doGoogleSearch(query, resultsToReturn, timePeriod, start*resultsPerPage)
            urls.extend(results)
            # print(f"Fetched {len(results)} results starting from {start*resultsPerPage}")
            remaining -= resultsToReturn
            time.sleep(2) # get by google rate limit
            
        print(numResults, " results fetched.")

    urls = list(set(urls))

    print("Duplicates removed, total unique results fetched:", len(urls))

    jobList = []
    jobListNoDetails = []
    jobListRejected = []

    print("Retreiving job information...")
    for url in urls:
        jobInfo = getJobInfo(url)
        if jobInfo:
            # print("Title: ", jobInfo['Job Title'], "Loc: ", jobInfo['Location'])
            if inUSA(jobInfo['Location']) and isRelevantRole(jobInfo['Job Title'], jobInfo['Job Description'], keywords):
                # print("YES")
                if jobInfo['Job Title'] != 'N/A': 
                    jobList.append(jobInfo)  
                else: 
                    jobListNoDetails.append(jobInfo)
            else: 
                jobListRejected.append(jobInfo)

    # sort the jobs by company name (alphabetically)
    jobList = sorted(jobList, key=lambda x: x['Company Name'])
    jobListNoDetails = sorted(jobListNoDetails, key=lambda x: x['Company Name'])
    jobListRejected = sorted(jobListRejected, key=lambda x: x['Company Name'])


    print(len(jobList), " relevant jobs found!")
    print(len(jobListNoDetails), " relevant (maybe) jobs found!")

    saveToExcel(jobList, jobListNoDetails, jobListRejected, timePeriod)

    return jobList, jobListNoDetails, jobListRejected

scrapeJobsMain()