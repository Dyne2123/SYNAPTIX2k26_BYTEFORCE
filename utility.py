import http.client
import urllib.parse
import json
import random
from main import JSEARCH
from main import send_whatsapp_message

def search_jobs(query, phonenumber, country="India", api_key=JSEARCH, max_jobs=1):
    """
    Fetch jobs from JSearch API and return a formatted string.
    - Prioritize jobs with qualifications.
    - Include job description, link, location, remote, employment type, posted date, salary.
    - Default country is India.
    """
    conn = http.client.HTTPSConnection("api.openwebninja.com")
    params = urllib.parse.urlencode({
        "query": query,
        "page": 1,
        "num_pages": 1
    })
    headers = {'x-api-key': api_key}
    conn.request("GET", f"/jsearch/search?{params}", headers=headers)
    res = conn.getresponse()
    data = res.read()
    conn.close()

    jobs_json = json.loads(data.decode("utf-8"))
    jobs_data = jobs_json.get("data", [])
    if not jobs_data:
        return "No jobs found."

    # Separate jobs with and without qualifications
    jobs_with_qual = []
    jobs_without_qual = []

    for job in jobs_data:
        jd = job.get("job_description")
        qual_list = job.get("job_highlights", {}).get("Qualifications", [])

        # If no explicit qualifications, try extracting from description
        if not qual_list and jd:
            qual_keywords = ["Education", "Required Skills", "Qualifications", 
                             "Experience", "Relevant Work Experience", "Skills", "Requirements"]
            jd_lines = [line.strip() for line in jd.split("\n") if line.strip()]
            qual_list = [line for line in jd_lines if any(k.lower() in line.lower() for k in qual_keywords)]

        if qual_list:
            jobs_with_qual.append((job, qual_list))
        elif jd:
            jobs_without_qual.append((job, []))  # Include description even if no quals

    # Prioritize jobs with qualifications
    prioritized_jobs = jobs_with_qual + jobs_without_qual
    if not prioritized_jobs:
        return "No jobs with description or qualifications found."

    # Randomize and pick up to max_jobs
    random.shuffle(prioritized_jobs)
    prioritized_jobs = prioritized_jobs[:max_jobs]

    formatted_jobs = []
    for job, qual_list in prioritized_jobs:
        title = job.get("job_title", "No title")
        company = job.get("employer_name", "Unknown company")
        link = job.get("job_google_link", job.get("job_apply_link", "#"))

        # Job description bullets
        jd = job.get("job_description", "")
        jd_lines = [line.strip() for line in jd.split("\n") if line.strip()]
        bullets = random.sample(jd_lines, min(3, len(jd_lines))) if jd_lines else []
        bullets_text = "\n".join(f"• {b}" for b in bullets) if bullets else "• No description available."

        # Qualifications
        if not qual_list:
            qual_list = ["No qualifications listed."]
        qual_text = "\n".join(f"• {q}" for q in qual_list)

        # Additional details with default country
        city = job.get("job_city")
        state = job.get("job_state")
        job_country = country or job.get("job_country") or "Unknown country"
        location_parts = [part for part in [city, state, job_country] if part]
        location = ", ".join(location_parts)

        remote_status = "Remote" if job.get("job_is_remote") else "On-site"
        employment_type = job.get("job_employment_type", "N/A")
        posted_date = job.get("job_posted_at", "N/A")
        salary = job.get("job_salary_string") or "Not disclosed"

        job_text = (
            f"**{title}** at **{company}**\n"
            f"{link}\n\n"
            f"{bullets_text}\n\n"
            f"**Qualifications:**\n{qual_text}\n\n"
            f"**Remote:** {remote_status}\n"
            f"**Employment Type:** {employment_type}\n"
            f"**Posted:** {posted_date}\n"
            f"**Salary:** {salary}"
        )
        formatted_jobs.append(job_text)

    final = "\n\n".join(formatted_jobs)
    send_whatsapp_message(phonenumber, final)