import re
import socket
import whois
import time
import requests
import numpy as np
from urllib.parse import urlparse
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# Suspicious words for phishing detection
suspicious_words = ["secure", "account", "webscr", "login", "ebayisapi", "signin", "banking"]

# Set up Selenium driver (headless mode)
options = webdriver.ChromeOptions()
options.add_argument("--headless")
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)


def extract_features(url):
    features = []
    
    # --- URL Based Features ---
    features.append(len(url))  # URLLength
    domain = urlparse(url).netloc
    features.append(len(domain))  # DomainLength
    
    # Check if the domain is an IP address
    try:
        socket.inet_aton(domain)
        features.append(1)  # IsDomainIP
    except:
        features.append(0)
    
    # Check URL similarity index (not implemented - set to 0)
    features.append(0)  # URLSimilarityIndex
    
    # Count special characters
    special_chars = ['?', '=', '&', '%', '$', '/', '!', '*', '#', ':', ',']
    features.append(sum([url.count(char) for char in special_chars]))  # CharContinuationRate
    
    # TLD Length
    tld = domain.split('.')[-1]
    features.append(len(tld))  # TLDLength
    
    # Number of Subdomains
    features.append(domain.count('.'))  # NoOfSubDomain
    
    # Check for obfuscation (like @, -, etc.)
    features.append(1 if '@' in url else 0)  # HasObfuscation
    features.append(url.count('@'))  # NoOfObfuscatedChar
    
    # Ratio of letters
    features.append(sum(c.isalpha() for c in url) / len(url))  # LetterRatioInURL
    features.append(sum(c.isdigit() for c in url) / len(url))  # DegitRatioInURL
    
    # HTTPS Check
    features.append(1 if url.startswith("https") else 0)  # IsHTTPS
    
    # --- Web Scraping Features ---
    try:
        # Launch the page using Selenium
        driver.get(url)
        time.sleep(2)
        page_source = driver.page_source
        
        # Parse the HTML
        soup = BeautifulSoup(page_source, 'html.parser')
        
        # Number of images
        features.append(len(soup.find_all('img')))  # NoOfImage
        
        # Number of JavaScript files
        features.append(len(soup.find_all('script')))  # NoOfJS
        
        # Number of CSS files
        features.append(len(soup.find_all('link', {'rel': 'stylesheet'})))  # NoOfCSS
        
        # Has Title
        features.append(1 if soup.title else 0)  # HasTitle
        
        # Length of title
        features.append(len(soup.title.string) if soup.title else 0)  # LargestLineLength
        
        # Has Favicon
        features.append(1 if soup.find('link', rel='icon') else 0)  # HasFavicon
        
        # Number of iframes (phishing sites use iframes often)
        features.append(len(soup.find_all('iframe')))  # NoOfiFrame
        
        # Number of popups (phishing indicator)
        features.append(len(driver.window_handles) - 1)  # NoOfPopup
        
        # Number of external form submissions
        external_forms = len([form for form in soup.find_all('form') 
                              if 'http' in form.get('action', '') and domain not in form.get('action', '')])
        features.append(external_forms)  # HasExternalFormSubmit
        
        # Number of hidden fields
        hidden_fields = len(soup.find_all('input', {'type': 'hidden'}))
        features.append(hidden_fields)  # HasHiddenFields
        
        # Number of social network links
        social_links = len([a['href'] for a in soup.find_all('a', href=True) 
                            if any(s in a['href'] for s in ['facebook', 'twitter', 'instagram'])])
        features.append(social_links)  # HasSocialNet
        
        # Number of URL redirects
        redirects = len(driver.get_log('performance'))  # This captures network redirects
        features.append(redirects)  # NoOfURLRedirect
        
    except Exception as e:
        # If scraping fails, zero-fill these features
        features.extend([0] * 14)
    
    # --- WHOIS Features ---
    try:
        whois_data = whois.whois(domain)
        creation_date = whois_data.creation_date
        
        # If multiple creation dates, take the first one
        if isinstance(creation_date, list):
            creation_date = creation_date[0]
        
        # Calculate domain age in days
        domain_age = (time.time() - creation_date.timestamp()) / (60*60*24)
        features.append(domain_age)  # Domain Age
    except:
        features.append(0)
    
    # --- Text-Based Features ---
    features.append(sum([1 for word in suspicious_words if word in url.lower()]))  # HasSuspiciousWords
    features.append(1 if 'bank' in url.lower() else 0)  # Bank
    features.append(1 if 'crypto' in url.lower() else 0)  # Crypto
    features.append(1 if 'pay' in url.lower() else 0)  # Pay
    
    return np.array(features)
