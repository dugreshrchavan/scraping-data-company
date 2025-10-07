from flask import Flask, jsonify, request
import requests
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor
import os
app = Flask(__name__)

COMPANIES = {
    "Narola Infotech": "https://narolainfotech.keka.com/careers",
    "Infosys": "https://www.infosys.com/careers",
    "Wipro": "https://careers.wipro.com",
    "Capgemini India": "https://www.capgemini.com/in-en/careers/",
    "Tata Elxsi": "https://www.tataelxsi.com/careers"
}



def scrape_narola(keyword):
    url = COMPANIES["Narola Infotech"]
    jobs = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        job_cards = soup.find_all("div", class_="career-title")  # job container

        for card in job_cards:
            title = card.get_text(strip=True)
            if keyword.lower() in title.lower():
                link_tag = card.find_parent("a")
                link = link_tag["href"] if link_tag else url
                jobs.append({
                    "Job Title": title,
                    "Company": "Narola Infotech",
                    "Location": "Surat",
                    "Salary": "Not specified",
                    "Apply Link": link
                })
    except Exception as e:
        print(f"Narola Error: {e}")
    return jobs

def scrape_infosys(keyword):
    url = COMPANIES["Infosys"]
    jobs = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        job_blocks = soup.find_all("div", class_="job-desc")  # example class

        for jb in job_blocks:
            title_tag = jb.find("h3")
            location_tag = jb.find("span", class_="location")
            link_tag = jb.find("a")

            title = title_tag.get_text(strip=True) if title_tag else "N/A"
            location = location_tag.get_text(strip=True) if location_tag else "Not specified"
            link = link_tag["href"] if link_tag else url

            if keyword.lower() in title.lower():
                jobs.append({
                    "Job Title": title,
                    "Company": "Infosys",
                    "Location": location,
                    "Salary": "Not specified",
                    "Apply Link": link
                })
    except Exception as e:
        print(f"Infosys Error: {e}")
    return jobs

def scrape_wipro(keyword):
    url = COMPANIES["Wipro"]
    jobs = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        job_blocks = soup.find_all("div", class_="opening")  # example container

        for jb in job_blocks:
            title = jb.get_text(strip=True)
            if keyword.lower() in title.lower():
                link_tag = jb.find("a")
                link = link_tag["href"] if link_tag else url
                jobs.append({
                    "Job Title": title,
                    "Company": "Wipro",
                    "Location": "India",
                    "Salary": "Not specified",
                    "Apply Link": link
                })
    except Exception as e:
        print(f"Wipro Error: {e}")
    return jobs

def scrape_capgemini(keyword):
    url = COMPANIES["Capgemini India"]
    jobs = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        job_links = soup.find_all("a", href=True)

        for a in job_links:
            title = a.get_text(strip=True)
            link = a["href"]
            if keyword.lower() in title.lower():
                if link.startswith("/"):
                    link = url.rstrip("/") + link
                jobs.append({
                    "Job Title": title,
                    "Company": "Capgemini India",
                    "Location": "Not specified",
                    "Salary": "Not specified",
                    "Apply Link": link
                })
    except Exception as e:
        print(f"Capgemini Error: {e}")
    return jobs

def scrape_tataelxsi(keyword):
    url = COMPANIES["Tata Elxsi"]
    jobs = []
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        soup = BeautifulSoup(r.text, "html.parser")
        job_links = soup.find_all("a", href=True)

        for a in job_links:
            title = a.get_text(strip=True)
            link = a["href"]
            if keyword.lower() in title.lower():
                if link.startswith("/"):
                    link = url.rstrip("/") + link
                jobs.append({
                    "Job Title": title,
                    "Company": "Tata Elxsi",
                    "Location": "Not specified",
                    "Salary": "Not specified",
                    "Apply Link": link
                })
    except Exception as e:
        print(f"Tata Elxsi Error: {e}")
    return jobs

# Map company to scraper function
SCRAPER_MAP = {
    "Narola Infotech": scrape_narola,
    "Infosys": scrape_infosys,
    "Wipro": scrape_wipro,
    "Capgemini India": scrape_capgemini,
    "Tata Elxsi": scrape_tataelxsi
}

# ---------------- Flask Route ----------------

@app.route("/jobs", methods=["GET"])
def get_jobs():
    keyword = request.args.get("keyword", "")
    if not keyword:
        return jsonify({"error": "Provide a keyword, e.g., ?keyword=Python"}), 400

    all_jobs = []

    # Use threads for faster scraping
    with ThreadPoolExecutor(max_workers=5) as executor:
        futures = [executor.submit(func, keyword) for func in SCRAPER_MAP.values()]
        for f in futures:
            try:
                all_jobs.extend(f.result())
            except Exception as e:
                print(f"Thread Error: {e}")

    # Optional: save to file
    with open("recruitment.txt", "w", encoding="utf-8") as f:
        for job in all_jobs:
            f.write(
                f"{job['Job Title']}\n{job['Company']}\n{job['Location']}\n{job['Salary']}\n{job['Apply Link']}\n{'-'*40}\n"
            )

    return jsonify(all_jobs)


if __name__ == '__main__':
    # Use Render's assigned PORT or default to 5000 locally
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
