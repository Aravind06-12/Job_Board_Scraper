
---

## 📜 `job_scraper.py`

Here’s your cleaned script, formatted for a GitHub repo:

```python
from bs4 import BeautifulSoup
import requests
import pandas as pd

def main():
    keywords = ["data analyst"]   # 👈 change keywords here
    keyword_str = "%2C".join(keywords)
    df = getting_data(keyword_str, max_jobs=30)   # 👈 limit jobs to run faster

    print("\n📌 Preview of first 10 jobs:\n")
    print(df.head(10))   # show first 10 rows

    df.to_csv("jobs.csv", index=False)
    print("\n✅ jobs.csv saved successfully.")

def getting_data(keywords, max_jobs=50):
    all_jobs = []
    jobs_scraped = 0
    n = 1
    condition = True
    PAGE_SIZE = 25   # TimesJobs default

    while condition:
        url = (
            f"https://www.timesjobs.com/candidate/job-search.html?"
            f"from=submit&actualTxtKeywords={keywords}&searchBy=0&rdoOperator=OR"
            f"&searchType=personalizedSearch&luceneResultSize={PAGE_SIZE}&postWeek=60"
            f"&txtKeywords={keywords}&pDate=I&sequence={n}&startPage=1"
        )

        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
        except requests.exceptions.RequestException as e:
            print(f"❌ Request failed: {e}")
            break

        soup = BeautifulSoup(response.text, 'lxml')

        total_tag = soup.find('span', id="totolResultCountsId")
        if total_tag:
            total = int(total_tag.text)
        else:
            print("⚠️ Could not find total results count. Exiting.")
            break

        jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
        jobs_scraped += len(jobs)
        print(f"Scraped {jobs_scraped}/{min(total, max_jobs)} jobs...")

        for job in jobs:
            name = job.find('h2').text.strip() if job.find('h2') else None
            company = job.find('h3', class_="joblist-comp-name").text.replace('\n', '').strip() if job.find('h3', class_="joblist-comp-name") else None
            skills = job.find('span', class_="srp-skills").text.strip() if job.find('span', class_="srp-skills") else None
            skills = ' '.join(skills.split()) if skills else None
            link = job.header.h2.a['href'] if job.header and job.header.h2 and job.header.h2.a else None

            location_tag = job.find('ul', class_='top-jd-dtl clearfix').find_all('li')
            location = location_tag[1].text.strip().replace('card_travel', '') if len(location_tag) > 1 else None

            all_jobs.append({
                'Position': name,
                'Company': company,
                'Location': location,
                'Skills': skills,
                'Link': link,
            })

        if jobs_scraped >= total or jobs_scraped >= max_jobs:
            condition = False
        else:
            n += 1

    return pd.DataFrame(all_jobs[:max_jobs])

if __name__ == '__main__':
    main()
