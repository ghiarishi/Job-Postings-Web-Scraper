# Job Postings Web Scraper

Job Postings Web Scraper is a Python-based tool designed to scrape job listings from Lever and Greenhouse job boards. It retrieves job titles, company names, locations, and job descriptions based on user-defined criteria and saves the results into an Excel file with separate sheets for relevant and potentially relevant job postings.

## Features

- Perform Google searches to find job postings on Lever and Greenhouse job boards.
- Filter jobs based on user-specified roles and time periods.
- Retrieve detailed job information including company name, job title, location, and job description.
- Save job listings to an Excel file with timestamps for easy tracking and review.
- Remove duplicate job listings and sort results alphabetically by company name.

## Prerequisites

- Python 3.6 or higher
- Required Python libraries (listed in `requirements.txt`)

## Installation

1. Clone the repository:
   ```sh
   git clone https://github.com/yourusername/Job-Postings-Web-Scraper.git
   cd Job-Postings-Web-Scraper
   ```

2. Install the required packages:
   ```sh
   pip install -r requirements.txt
   ```

## Usage

1. Run the script:
   ```sh
   python jobScraper.py
   ```

2. Input the required information:
   - Number of results to fetch: Enter 'max' to fetch as many results as possible or an integer to specify the exact number.
   - Time period for the results: Specify 'h' for hour, 'd' for day, 'w' for week, 'm' for month, or 'y' for year.
   - Roles of interest: Specify roles like 'sde' (Software Development Engineer), 'aiml' (AI/ML), 'cv' (Computer Vision), 'nlp' (Natural Language Processing), 'robo' (Robotics), or 'all' for all roles.

3. Review the results:
   - The script will fetch and display the number of job listings retrieved, remove duplicates, and show the number of relevant and potentially relevant job postings.

4. Output:
   - The job listings will be saved to an Excel file named in the format `jobListings-<timePeriod>-<HH-MM, DD-MM-YYYY>.xlsx` with two sheets: 'Relevant Jobs' and 'Relevant (Maybe) Jobs'.

## Code Overview

### Main Components

- `keywordsDict`: Dictionary mapping role abbreviations to relevant keywords.
- `selectRoles(whichRoles)`: Function to select and return keywords based on user input roles.
- `doGoogleSearch(query, numResults, timePeriod, start)`: Function to perform Google search and return job URLs.
- `cleanURL(job_url)`: Function to clean and standardize job URLs.
- `getJobInfo(url)`: Function to retrieve job details from a given URL.
- `inUSA(location)`: Function to check if the job location is in the USA.
- `isRelevantRole(jobTitle, keywords)`: Function to check if the job title matches relevant keywords.
- `saveToExcel(jobList, jobListNoDetails, timePeriod)`: Function to save job listings to an Excel file.

### Example Workflow

## Authors

- Rishi Ghia - [ghiarishi](https://github.com/ghiarishi)

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.

## Acknowledgments

- Inspiration and initial concept by Rishi Ghia.
- Special thanks to the open-source community for the libraries used in this project.
```
