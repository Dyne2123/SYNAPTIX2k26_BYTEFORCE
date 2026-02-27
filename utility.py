import http.client
import urllib.parse
import json
import random
from main import JSEARCH
from main import send_whatsapp_message
import requests

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

        
        if not qual_list and jd:
            qual_keywords = ["Education", "Required Skills", "Qualifications", 
                             "Experience", "Relevant Work Experience", "Skills", "Requirements"]
            jd_lines = [line.strip() for line in jd.split("\n") if line.strip()]
            qual_list = [line for line in jd_lines if any(k.lower() in line.lower() for k in qual_keywords)]

        if qual_list:
            jobs_with_qual.append((job, qual_list))
        elif jd:
            jobs_without_qual.append((job, [])) 

    
    prioritized_jobs = jobs_with_qual + jobs_without_qual
    if not prioritized_jobs:
        return "No jobs with description or qualifications found."

    
    random.shuffle(prioritized_jobs)
    prioritized_jobs = prioritized_jobs[:max_jobs]

    formatted_jobs = []
    for job, qual_list in prioritized_jobs:
        title = job.get("job_title", "No title")
        company = job.get("employer_name", "Unknown company")
        link = job.get("job_google_link", job.get("job_apply_link", "#"))

       
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

from main import METAL
BASE_URL = "https://api.metalpriceapi.com/v1/latest"
api= METAL

def get_gold_price():
    params = {
        "api_key": api,
        "base": "XAU",     
        "currencies": "INR"  
    }
    
    response = requests.get(BASE_URL, params=params)
    print(response.json())
    if response.status_code != 200:
        return f" API Error: {response.status_code}"

    data = response.json()

    if not data.get("success"):
        return " API returned failure"

    rates = data.get("rates", {})
    inr_per_ounce = rates.get("INR")

    if not inr_per_ounce:
        return " No INR rate found"

    # Convert ounce → gram
    price_per_gram = inr_per_ounce / 31.1035

    return f"🪙 Gold Price: ₹{price_per_gram:.2f} per gram"



import secrets
import string

def generate_password(length=16):
    if length < 8:
        raise ValueError("Password length should be at least 8 characters")

    # Character sets
    lowercase = string.ascii_lowercase
    uppercase = string.ascii_uppercase
    digits = string.digits
    special = string.punctuation

    # Ensure password contains at least one from each category
    password = [
        secrets.choice(lowercase),
        secrets.choice(uppercase),
        secrets.choice(digits),
        secrets.choice(special)
    ]

    # Fill the rest of the password length
    all_chars = lowercase + uppercase + digits + special
    password += [secrets.choice(all_chars) for _ in range(length - 4)]

    # Shuffle the password
    secrets.SystemRandom().shuffle(password)

    return ''.join(password)

def fetch_crypto_data(params):
    from main import CRYPTO
    api_key = CRYPTO
    """
    Base CoinMarketCap API caller.
    Accepts dynamic params and returns JSON data.
    """
    url = "https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest"

    headers = {
        "Accepts": "application/json",
        "X-CMC_PRO_API_KEY": api_key,
    }

    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()

    except requests.exceptions.RequestException as e:
        return {"error": str(e)}
    
def get_top_10(currency="INR"):
    params = {
        "start": "1",
        "limit": "10",
        "convert": currency
    }

    data = fetch_crypto_data(params)

    if "error" in data:
        return data["error"]

    result = []
    for coin in data["data"]:
        price = coin["quote"][currency]["price"]
        result.append(
            f"{coin['cmc_rank']}. {coin['name']} ({coin['symbol']}) : {currency} {price:,.2f}"
        )
    res = "\n".join(result)
    return res

import yfinance as yf

def get_stock_price(company_name):
    try:
        # Search company
        search = yf.Search(company_name)
        results = search.quotes

        if not results:
            return "Company not found."

        ticker_symbol = results[0]["symbol"]
        short_name = results[0].get("shortname", ticker_symbol)

        stock = yf.Ticker(ticker_symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return "Price data not available."

        price = hist["Close"].iloc[-1]

        # Detect currency
        info = stock.info
        currency = info.get("currency", "USD")

        # If already INR (like NSE stocks)
        if currency == "INR":
            return f"{short_name} ({ticker_symbol}) → ₹{price:,.2f}"

        # Convert USD → INR
        usd_inr = yf.Ticker("USDINR=X").history(period="1d")["Close"].iloc[-1]
        price_inr = price * usd_inr

        return f"{short_name} ({ticker_symbol}) → ₹{price_inr:,.2f}"

    except Exception as e:
        return f"Error: {str(e)}"

