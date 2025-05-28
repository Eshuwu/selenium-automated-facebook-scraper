import os
import time
import random
import json
import requests
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Add drivers to path
os.environ['PATH'] += r"""C:\seldrivers"""

# JSONBin configuration
JSONBIN_API_KEY = "UPLOAD YOUR MASTER API KEY HERE"  
JSONBIN_BIN_ID = "YOUR_BIN_ID"  # Replace with your bin ID (optional for new bins)
JSONBIN_BASE_URL = "https://api.jsonbin.io/v3"

# Local backup file paths
BACKUP_JSON_PATH = r"C:\Users\xyz\OneDrive\Documents\scraped_data_backup.json" 
BACKUP_CSV_PATH = r"C:\Users\xyz\OneDrive\Documents\scraped_data_backup.csv"

# Setup Chrome options to mimic human behavior and avoid detection
chrome_options = Options()
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option("useAutomationExtension", False)
chrome_options.add_argument("--disable-notifications")  # Disable notifications

# User agent to appear more like a regular browser
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
chrome_options.add_argument(f'user-agent={user_agent}')


def create_jsonbin_bin(api_key, bin_name="Facebook Scraped Data"):
    """Create a new JSONBin bin and return the bin ID"""
    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }

    initial_data = {
        "scraped_data": [],
        "metadata": {
            "created_at": time.strftime("%Y-%m-%d %H:%M:%S"),
            "total_records": 0,
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S")
        }
    }

    try:
        response = requests.post(
            f"{JSONBIN_BASE_URL}/b",
            json=initial_data,
            headers=headers
        )

        if response.status_code == 200:
            bin_id = response.json()["metadata"]["id"]
            print(f"✓ Created new JSONBin with ID: {bin_id}")
            return bin_id
        else:
            print(f"Error creating bin: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error creating JSONBin: {str(e)}")
        return None


def save_to_jsonbin(data, api_key, bin_id=None):
    """Save data to JSONBin"""
    if not data:
        print("No data to save to JSONBin")
        return False, None

    # Filter out group pages
    filtered_data = [item for item in data if not item.get("is_group", False)]

    if not filtered_data:
        print("No valid data found after filtering out Facebook groups")
        return False, None

    # Prepare data for JSONBin
    jsonbin_data = {
        "scraped_data": filtered_data,
        "metadata": {
            "total_records": len(filtered_data),
            "last_updated": time.strftime("%Y-%m-%d %H:%M:%S"),
            "scraping_session": time.strftime("%Y%m%d_%H%M%S")
        }
    }

    headers = {
        "Content-Type": "application/json",
        "X-Master-Key": api_key
    }

    try:
        if bin_id:
            # Update existing bin
            response = requests.put(
                f"{JSONBIN_BASE_URL}/b/{bin_id}",
                json=jsonbin_data,
                headers=headers
            )
            action = "Updated"
        else:
            # Create new bin
            response = requests.post(
                f"{JSONBIN_BASE_URL}/b",
                json=jsonbin_data,
                headers=headers
            )
            action = "Created"

        if response.status_code == 200:
            response_data = response.json()
            actual_bin_id = response_data["metadata"]["id"]
            print(f"✓ {action} JSONBin successfully!")
            print(f"  Bin ID: {actual_bin_id}")
            print(f"  Records saved: {len(filtered_data)}")
            print(f"  JSONBin URL: https://jsonbin.io/{actual_bin_id}")
            return True, actual_bin_id
        else:
            print(f"Error saving to JSONBin: {response.status_code} - {response.text}")
            return False, bin_id

    except Exception as e:
        print(f"Error saving to JSONBin: {str(e)}")
        return False, bin_id


def save_local_backup(data, count):
    """Save local backup files (JSON and CSV)"""
    if not data:
        return False

    # Filter out group pages
    filtered_data = [item for item in data if not item.get("is_group", False)]

    if not filtered_data:
        return False

    success = False

    try:
        # Ensure directories exist
        Path(os.path.dirname(BACKUP_JSON_PATH)).mkdir(parents=True, exist_ok=True)
        Path(os.path.dirname(BACKUP_CSV_PATH)).mkdir(parents=True, exist_ok=True)

        # Save JSON backup
        try:
            backup_data = {
                "scraped_data": filtered_data,
                "metadata": {
                    "total_records": len(filtered_data),
                    "backup_created": time.strftime("%Y-%m-%d %H:%M:%S"),
                    "scraping_session": time.strftime("%Y%m%d_%H%M%S")
                }
            }

            with open(BACKUP_JSON_PATH, 'w', encoding='utf-8') as f:
                json.dump(backup_data, f, indent=2, ensure_ascii=False)
            print(f"✓ JSON backup saved to {BACKUP_JSON_PATH}")
            success = True
        except Exception as json_error:
            print(f"Error saving JSON backup: {str(json_error)}")

        # Save CSV backup
        try:
            import pandas as pd
            df = pd.DataFrame(filtered_data)
            df.to_csv(BACKUP_CSV_PATH, index=False)
            print(f"✓ CSV backup saved to {BACKUP_CSV_PATH}")
            success = True
        except Exception as csv_error:
            print(f"Error saving CSV backup: {str(csv_error)}")

    except Exception as path_error:
        print(f"Path error: {str(path_error)}")
        # Try saving to current directory as fallback
        try:
            with open(f"scraped_data_backup_{count}.json", 'w', encoding='utf-8') as f:
                json.dump({"scraped_data": filtered_data}, f, indent=2)
            print(f"✓ Saved JSON backup to current directory")
            success = True
        except Exception as fallback_error:
            print(f"Error saving to current directory: {str(fallback_error)}")

    return success


def save_data(data, count, api_key, bin_id=None):
    """Main save function that saves to both JSONBin and local backup"""
    if not data:
        print("No data to save")
        return False, None

    print(f"\n--- Saving {len(data)} records ---")

    # Save to JSONBin
    jsonbin_success, updated_bin_id = save_to_jsonbin(data, api_key, bin_id)

    # Save local backup regardless of JSONBin success
    backup_success = save_local_backup(data, count)

    if jsonbin_success:
        print("✓ Data successfully saved to JSONBin")
    elif backup_success:
        print("JSONBin failed, but local backup saved")
    else:
        print("Both JSONBin and local backup failed")

    return jsonbin_success or backup_success, updated_bin_id


# Function to mimic human-like interactions
def human_like_interaction(driver, more_random=False):
    """Perform random human-like actions to avoid detection"""
    # Random pause between actions
    time.sleep(random.uniform(1.5, 4.0) if more_random else random.uniform(1.0, 2.5))

    # Random scrolling
    if random.choice([True, False, True]):  # 2/3 chance to scroll
        scroll_amount = random.randint(-150, 300)
        driver.execute_script(f"window.scrollBy(0, {scroll_amount});")
        time.sleep(random.uniform(0.5, 1.5))

    # Sometimes move mouse (simulated by more scrolling)
    if more_random and random.choice([True, False]):
        small_scroll = random.randint(-50, 50)
        driver.execute_script(f"window.scrollBy(0, {small_scroll});")


# Function to handle Facebook login popup with interactive fallback
def handle_facebook_popup(driver):
    """Handle Facebook login popup with multiple strategies and manual fallback"""
    print("Checking for login popup...")
    try:
        # Wait for page to load
        time.sleep(2)
        close_button_found = False

        # Method 1: Using aria-label
        close_buttons = driver.find_elements(By.XPATH,
                                             "//div[contains(@aria-label, 'Close') or contains(@aria-label, 'close')] | " +
                                             "//button[contains(@aria-label, 'Close') or contains(@aria-label, 'close')]")
        if close_buttons and not close_button_found:
            try:
                print("Found close button with aria-label, clicking...")
                close_buttons[0].click()
                close_button_found = True
                print("✓ Closed popup using aria-label")
                time.sleep(1)
            except Exception as e:
                print(f"  Failed to click aria-label button: {str(e)}")

        # Method 2: Using the X symbol
        if not close_button_found:
            close_x_buttons = driver.find_elements(By.XPATH,
                                                   "//div[text()='×'] | //span[text()='×'] | //i[text()='×'] | " +
                                                   "//div[contains(text(), '×')] | //div[contains(@aria-label, 'Close')]")
            if close_x_buttons:
                try:
                    print("Found × symbol button, clicking...")
                    close_x_buttons[0].click()
                    close_button_found = True
                    print("✓ Closed popup using × symbol")
                    time.sleep(1)
                except Exception as e:
                    print(f"  Failed to click × button: {str(e)}")

        # Method 3: Facebook-specific selectors
        if not close_button_found:
            fb_close_selectors = [
                "div.x92rtbv.x1lliihq",
                "div.x1i10hfl.x1qjc9v5.xjbqb8w",
                "div.x1ey2m1c.xds687c.x5yr21d",
                "div[role='button'][tabindex='0']"
            ]
            for selector in fb_close_selectors:
                try:
                    close_elements = driver.find_elements(By.CSS_SELECTOR, selector)
                    for element in close_elements:
                        if element.is_displayed():
                            print(f"Found close button with selector {selector}, clicking...")
                            element.click()
                            close_button_found = True
                            print(f"✓ Closed popup using selector {selector}")
                            time.sleep(1)
                            break
                    if close_button_found:
                        break
                except Exception as e:
                    print(f"  Failed with selector {selector}: {str(e)}")

        # Method 4: Try to click outside the popup
        if not close_button_found:
            try:
                # Try clicking at the top of the page outside popup
                print("Trying to click outside popup...")
                driver.execute_script(
                    "document.body.dispatchEvent(new MouseEvent('click', { clientX: 10, clientY: 10 }));")
                time.sleep(1)
                close_button_found = True
                print("✓ Clicked outside popup")
            except Exception as e:
                print(f"  Failed to click outside: {str(e)}")

        # Method 5: Use Escape key
        if not close_button_found:
            try:
                print("Pressing Escape key...")
                webdriver.ActionChains(driver).send_keys(Keys.ESCAPE).perform()
                time.sleep(1)
                close_button_found = True
                print("✓ Sent Escape key")
            except Exception as e:
                print(f"  Failed to send Escape: {str(e)}")

        # Manual intervention if automated methods fail
        if not close_button_found:
            print("\n ATTENTION NEEDED: Could not automatically close the Facebook login popup")
            print("Please manually close the popup now. You have 15 seconds...")
            time.sleep(15)  # Give user time to intervene
            print("Continuing...")

    except Exception as e:
        print(f"Error in popup handler: {str(e)}")
        print("Continuing script execution...")


# Enhanced function to extract details from a Facebook page
def extract_facebook_page_details(driver):
    """Extract contact details from Facebook page with improved logging and scrolling"""
    details = {
        "page_name": "Not found",
        "phone_number": "Not found",
        "website": "Not found",
        "address": "Not found",
        "email": "Not found",
        "description": "Not found",
        "url": driver.current_url,
        "data_completeness": 0,  # Track how complete the data is
        "scraped_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }

    print(f"\nExtracting data from: {driver.current_url}")

    # Wait for the page to load
    time.sleep(random.uniform(3.0, 5.0))

    # Check if this is a group page - if so, skip it
    if "/groups/" in driver.current_url:
        print("Facebook group detected, skipping...")
        details["is_group"] = True
        return details

    # Handle login popup
    handle_facebook_popup(driver)

    # Scroll down to make sure content is loaded
    print("Scrolling down to load content...")
    for _ in range(3):
        driver.execute_script("window.scrollBy(0, 300);")
        time.sleep(random.uniform(0.7, 1.5))

    try:
        # Get page name from h1
        try:
            page_name_elements = driver.find_elements(By.TAG_NAME, "h1")
            if page_name_elements:
                details["page_name"] = page_name_elements[0].text
                print(f"Found page name: {details['page_name']}")
        except Exception as e:
            print(f"Error getting page name: {str(e)}")

        # Try alternative method for page name
        if details["page_name"] == "Not found":
            try:
                alt_name_elements = driver.find_elements(By.CSS_SELECTOR, "span.x193iq5w.xeuugli")
                for element in alt_name_elements:
                    if element.text and len(element.text) > 3:
                        details["page_name"] = element.text
                        print(f"Found alternative page name: {details['page_name']}")
                        break
            except Exception as e:
                print(f"Error with alternative page name: {str(e)}")

        # Look for the About tab and click it if present
        try:
            about_tabs = driver.find_elements(By.XPATH, "//span[text()='About']/..")
            if about_tabs:
                print("Found About tab, clicking it...")
                about_tabs[0].click()
                time.sleep(3)  # Wait for About page to load
                print("Clicked About tab")
            else:
                print("About tab not found")
        except Exception as e:
            print(f"Error clicking About tab: {str(e)}")

        # Find contact info section
        contact_sections = driver.find_elements(By.XPATH,
                                                "//span[text()='Contact Info' or contains(text(), 'Contact')]/../..")
        if contact_sections:
            print("Found Contact Info section")

        # Extract address with multiple approaches
        try:
            # Look for elements with address-like content
            address_patterns = [
                "//span[contains(text(), 'Toronto') or contains(text(), 'Ontario') or contains(text(), 'Canada')]",
                "//span[contains(text(), 'St') or contains(text(), 'Ave') or contains(text(), 'Road')]",
                "//div[contains(@class, 'x193iq5w')]//span[contains(text(), '#') or contains(text(), 'Street')]"
            ]

            for pattern in address_patterns:
                address_elements = driver.find_elements(By.XPATH, pattern)
                for element in address_elements:
                    text = element.text
                    if ('#' in text or 'Toronto' in text or 'Ontario' in text or 'Canada' in text or
                            'Ave' in text or 'St' in text or 'Road' in text):
                        details["address"] = text
                        print(f"Found address: {details['address']}")
                        break
                if details["address"] != "Not found":
                    break

        except Exception as addr_err:
            print(f"Error extracting address: {str(addr_err)}")

        # Extract phone number using multiple strategies
        try:
            phone_patterns = [
                "//span[contains(text(), '+1') or contains(text(), '(') or contains(text(), '416') or contains(text(), '647')]",
                "//div[contains(@class, 'x9f619')]//span[contains(text(), '-') and string-length() > 8]"
            ]

            for pattern in phone_patterns:
                phone_elements = driver.find_elements(By.XPATH, pattern)
                for element in phone_elements:
                    text = element.text
                    # Check if it looks like a phone number
                    if ('+1' in text or '(' in text or '-' in text or
                            any(area_code in text for area_code in ['416', '647', '905', '289'])):
                        details["phone_number"] = text
                        print(f"Found phone number: {details['phone_number']}")
                        break
                if details["phone_number"] != "Not found":
                    break

        except Exception as phone_err:
            print(f"Error extracting phone number: {str(phone_err)}")

        # Extract website
        try:
            website_elements = driver.find_elements(By.XPATH,
                                                    "//a[contains(@href, 'http') and not(contains(@href, 'facebook.com'))]")
            for element in website_elements:
                href = element.get_attribute('href')
                if href and 'facebook.com' not in href and 'fb.com' not in href:
                    if 'l.facebook.com/l.php?' in href:
                        # This is a redirected link, try to extract the actual URL
                        try:
                            import urllib.parse
                            parsed = urllib.parse.urlparse(href)
                            query = urllib.parse.parse_qs(parsed.query)
                            if 'u' in query:
                                href = query['u'][0]
                        except:
                            pass
                    details["website"] = href
                    print(f"Found website: {details['website']}")
                    break
        except Exception as web_err:
            print(f"Error extracting website: {str(web_err)}")

        # Extract email
        try:
            # Look for mailto links
            email_elements = driver.find_elements(By.XPATH, "//a[contains(@href, 'mailto:')]")
            if email_elements:
                details["email"] = email_elements[0].get_attribute('href').replace('mailto:', '')
                print(f"Found email: {details['email']}")
            else:
                # Try to find spans that contain @ symbol
                email_spans = driver.find_elements(By.XPATH,
                                                   "//span[contains(text(), '@') and contains(text(), '.')]")
                for span in email_spans:
                    text = span.text
                    if '@' in text and '.' in text and not text.startswith('@'):  # Filter out @mentions
                        details["email"] = text
                        print(f"Found email: {details['email']}")
                        break
        except Exception as email_err:
            print(f"Error extracting email: {str(email_err)}")

        # Extract organization description
        try:
            # Various places to look for descriptions
            description_patterns = [
                "//div[text()='About']/../following-sibling::div[1]",
                "//span[text()='About']/../following-sibling::div[1]",
                "//div[contains(@class, 'xdj266r')]//span[string-length() > 20]"
            ]

            for pattern in description_patterns:
                desc_elements = driver.find_elements(By.XPATH, pattern)
                for element in desc_elements:
                    text = element.text
                    if len(text) > 20:  # Reasonable length for a description
                        details["description"] = text
                        print(f"Found description: {details['description'][:30]}...")
                        break
                if details["description"] != "Not found":
                    break
        except Exception as desc_err:
            print(f"Error extracting description: {str(desc_err)}")

        # Calculate data completeness
        fields = ["page_name", "phone_number", "website", "address", "email", "description"]
        found_fields = sum(1 for field in fields if details[field] != "Not found")
        details["data_completeness"] = round((found_fields / len(fields)) * 100)
        print(f"Data completeness: {details['data_completeness']}%")

    except Exception as e:
        print(f"Error extracting page details: {str(e)}")

    return details


# Main execution with error handling and progressive saving
def main():
    driver = None
    all_brand_data = []
    current_bin_id = JSONBIN_BIN_ID

    # Check if API key is set
    if not JSONBIN_API_KEY or JSONBIN_API_KEY == "YOUR_JSONBIN_API_KEY":
        print("Warning: JSONBin API key not set!")
        print("Please update JSONBIN_API_KEY in the script with your actual API key.")
        print("You can get a free API key from https://jsonbin.io")
        print("The script will continue with local backup only.")
        use_jsonbin = False
    else:
        use_jsonbin = True
        print(f"✓ JSONBin API key configured")

    try:
        print("Starting Facebook brand scraper with JSONBin storage...")

        # Create a new bin if no bin ID is provided
        if use_jsonbin and (not current_bin_id or current_bin_id == "YOUR_BIN_ID"):
            print("Creating new JSONBin...")
            current_bin_id = create_jsonbin_bin(JSONBIN_API_KEY)
            if current_bin_id:
                print(f" New bin created with ID: {current_bin_id}")
                print(" Save this Bin ID for future use!")
            else:
                print(" Failed to create JSONBin, using local backup only")
                use_jsonbin = False

        # Initialize the Chrome driver
        driver = webdriver.Chrome(options=chrome_options)

        # Modify Navigator properties to avoid detection
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")

        # Start with Bing instead of Google (less strict bot detection)
        driver.get("https://www.bing.com")
        print("\nBrowser opened. If a CAPTCHA appears, please complete it manually.")
        print("You have 20 seconds to handle any verification...")
        time.sleep(20)  # Give user time to handle any CAPTCHA

        # Set search parameters
        search_query = "clothing brands in Canada site:facebook.com"
        max_pages = 5  # Maximum number of search result pages to process
        results_per_page = 10  # Approximate results per page for tracking

        # Wait for search box
        search_box = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "sb_form_q"))
        )

        # Enter search query with human-like typing
        search_box.clear()
        for char in search_query:
            search_box.send_keys(char)
            time.sleep(random.uniform(0.05, 0.15))

        human_like_interaction(driver)
        search_box.send_keys(Keys.RETURN)

        # Process search results pages
        page_num = 1
        results_processed = 0

        print(f"\nProcessing up to {max_pages} pages of search results...")
        print(f"Will save data every {results_per_page} results and at the end of each page")

        while page_num <= max_pages:
            print(f"\n=== Processing search results page {page_num} ===")

            # Wait for results to load
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ol#b_results li.b_algo"))
            )

            human_like_interaction(driver)

            # Get all search result links
            search_results = driver.find_elements(By.CSS_SELECTOR, "ol#b_results li.b_algo h2 a")
            print(f"Found {len(search_results)} results on this page")

            # Process each result
            for i, link_element in enumerate(search_results):
                try:
                    # Extract the link info
                    link_text = link_element.text
                    link_href = link_element.get_attribute('href')
                    results_processed += 1

                    print(f"\nProcessing result {results_processed} ({page_num}.{i + 1}): {link_text}")

                    # Skip if not a Facebook page
                    if "facebook.com" not in link_href:
                        print("Not a Facebook link, skipping")
                        continue

                    # Skip groups early
                    if "/groups/" in link_href:
                        print("Facebook group detected, skipping")
                        continue

                    # Store current window handle
                    main_window = driver.current_window_handle

                    # Open link in new tab
                    driver.execute_script("arguments[0].setAttribute('target', '_blank');", link_element)
                    human_like_interaction(driver)
                    link_element.click()

                    # Switch to the new tab
                    time.sleep(2)
                    all_handles = driver.window_handles
                    for handle in all_handles:
                        if handle != main_window:
                            driver.switch_to.window(handle)
                            break

                    # Extract page details
                    details = extract_facebook_page_details(driver)
                    details["search_result_title"] = link_text
                    all_brand_data.append(details)

                    # Close tab and return to main window
                    driver.close()
                    driver.switch_to.window(main_window)
                    human_like_interaction(driver, more_random=True)

                    # Save progress every 10 results
                    if results_processed % results_per_page == 0:
                        print(f"\n--- Saving progress after {results_processed} results ---")
                        if use_jsonbin:
                            success, updated_bin_id = save_data(all_brand_data, results_processed, JSONBIN_API_KEY,
                                                                current_bin_id)
                            if updated_bin_id:
                                current_bin_id = updated_bin_id
                        else:
                            save_local_backup(all_brand_data, results_processed)

                except Exception as e:
                    print(f"Error processing result: {str(e)}")
                    # Try to recover by returning to main window
                    try:
                        all_handles = driver.window_handles
                        if main_window in all_handles:
                            driver.switch_to.window(main_window)
                        else:
                            # If main window is lost, restart from Bing
                            print("Lost main window, restarting search")
                            driver.get("https://www.bing.com")
                            search_box = WebDriverWait(driver, 10).until(
                                EC.presence_of_element_located((By.ID, "sb_form_q"))
                            )
                            search_box.clear()
                            search_box.send_keys(search_query)
                            search_box.send_keys(Keys.RETURN)
                    except Exception as recovery_error:
                        print(f"Recovery failed: {str(recovery_error)}")
                        # Last resort - restart browser
                        try:
                            driver.quit()
                            driver = webdriver.Chrome(options=chrome_options)
                            driver.get("https://www.bing.com")
                        except:
                            print("Critical error - saving data and exiting")
                            if use_jsonbin:
                                save_data(all_brand_data, results_processed, JSONBIN_API_KEY, current_bin_id)
                            else:
                                save_local_backup(all_brand_data, results_processed)
                            return

            # Save data at the end of each page
            print(f"\n--- Saving progress after page {page_num} ---")
            if use_jsonbin:
                success, updated_bin_id = save_data(all_brand_data, page_num * 10, JSONBIN_API_KEY, current_bin_id)
                if updated_bin_id:
                    current_bin_id = updated_bin_id
            else:
                save_local_backup(all_brand_data, page_num * 10)

            # Try to go to next page
            try:
                next_buttons = driver.find_elements(By.XPATH, "//a[contains(@title, 'Next page')]")
                if next_buttons:
                    human_like_interaction(driver)
                    next_buttons[0].click()
                    page_num += 1
                else:
                    print("No more search result pages")
                    break
            except Exception as e:
                print(f"Error navigating to next page: {str(e)}")
                break

        # Final save
        print("\n=== Scraping complete ===")
        print(f"Processed {results_processed} results across {page_num} pages")

        if use_jsonbin:
            success, final_bin_id = save_data(all_brand_data, results_processed, JSONBIN_API_KEY, current_bin_id)
            if success and final_bin_id:
                print(f"\n All data saved successfully!")
                print(f"JSONBin URL: https://jsonbin.io/{final_bin_id}")
                print(f" Bin ID: {final_bin_id}")
                print("Save the Bin ID above for future access to your data!")
        else:
            save_local_backup(all_brand_data, results_processed)
            print(f"\n All data saved to local backup files!")

    except Exception as e:
        print(f"An error occurred in main execution: {str(e)}")
        # Try to save whatever data we have
        if all_brand_data:
            print("Attempting to save collected data before exit...")
            if use_jsonbin:
                save_data(all_brand_data, len(all_brand_data), JSONBIN_API_KEY, current_bin_id)
            else:
                save_local_backup(all_brand_data, len(all_brand_data))

    finally:
        print("\nScript complete. Press Enter to close the browser...")
        input()
        if driver:
            driver.quit()


def read_from_jsonbin(api_key, bin_id):
    """Read data from JSONBin (utility function)"""
    headers = {
        "X-Master-Key": api_key
    }

    try:
        response = requests.get(
            f"{JSONBIN_BASE_URL}/b/{bin_id}/latest",
            headers=headers
        )

        if response.status_code == 200:
            data = response.json()
            print(f"✓ Successfully retrieved data from JSONBin")
            print(f"  Total records: {data.get('metadata', {}).get('total_records', 'Unknown')}")
            return data
        else:
            print(f"Error reading from JSONBin: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"Error reading from JSONBin: {str(e)}")
        return None


if __name__ == "__main__":
    print("=== Facebook Brand Scraper with JSONBin Storage ===")
    print("\n Setup Instructions:")
    print("1. Sign up for a free JSONBin account at https://jsonbin.io")
    print("2. Get your API key from the dashboard")
    print("3. Update JSONBIN_API_KEY in this script")
    print("4. Optionally set JSONBIN_BIN_ID if you want to use an existing bin")
    print("\n🚀 Starting scraper...")
    main()
