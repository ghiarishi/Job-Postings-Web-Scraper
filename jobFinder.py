import requests
import pandas as pd

def fetch_greenhouse_jobs(board_token):
    url = f"https://boards-api.greenhouse.io/v1/boards/{board_token}/jobs"
    response = requests.get(url)
    jobs_data = response.json()

    job_list = []
    for job in jobs_data['jobs']:
        job_list.append({
            'Title': job['title'],
            'Location': job.get('location', {}).get('name', 'Remote/Not specified'),
            'URL': job['absolute_url']
        })

    return job_list

def main():
    board_token = 'waymo'  # Replace this with the actual board token
    job_data = fetch_greenhouse_jobs(board_token)

    # Convert job data to a DataFrame and save to Excel
    df = pd.DataFrame(job_data)
    df.to_excel('greenhouse_jobs.xlsx', index=False)
    print("Data has been written to 'greenhouse_jobs.xlsx'")

if __name__ == "__main__":
    main()
