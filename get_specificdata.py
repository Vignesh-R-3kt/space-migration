import datetime
from bs4 import BeautifulSoup
import requests
import re
import openpyxl

# Set your Confluence server URL and API token
url = "https://cxapplucy.atlassian.net/wiki"
username = "mail6gowthamdwd@gmail.com"
password = "ATATT3xFfGF0Ah_u6_39uxUtrsdifcJzr5zq_e_ENlniqUr0ua-v_1--lvJwuigsAmv7sWe_yDgfR5beluvu5xSYnA7X_A-ZK3eT2gcQg9JZfCV3Jk2OjjkzzsOD0_TIpBXjQST-kJGR3SVxgN6VMx_FzXmEOpuWnlH74A-DUN81_464R45dgqE=FACB6C0F"
# Set the space key for the space you want to retrieve pages from
space_key = "DATA"

# Initialize variables

start_val = 0
page_size = 10000  # Adjust this based on your needs
headers = {
    "Content-Type": "application/json",
}

def get_target_pages(space_key):
    start_val = 0
    all_pages = []
    print('statted page titles')
    while True:
        # Define the API endpoint to retrieve pages in a space
        api_endpoint = f"{url}/rest/api/content?spaceKey={space_key}&start={start_val}&limit={page_size}"

        # Set up headers for authentication

        # Make the API request
        response = requests.get(api_endpoint, headers=headers, auth=(username, password))

        if response.status_code == 200:
            # Parse the JSON response and append pages to the result list
            page_data = response.json()
            all_pages.extend(page_data.get("results", []))

            # Check if there are more pages to fetch
            if not page_data.get("isLastPage", True):
                start_val += page_size
            else:
                break
        else:
            print(f"Failed to retrieve pages. Status code: {response.status_code}")
            break
    mapped_pageIds = {}
    for page in all_pages:
        mapped_pageIds.update({page['title']: page['id']})
    return mapped_pageIds


def validate_attachements(page_id):
    response = requests.get(f"{url}/rest/api/content/{page_id}/child/attachment",
                             headers=headers, auth=(username, password))
    
    if response.status_code == 200:
        data = response.json()
        list_attachments = data.get('results')
        page_attachments = {}
        for attachment in list_attachments:
            page_attachments.update({attachment['title']: 
                                     [attachment['id'], 
                                      attachment['extensions']['fileSize']]
                                    }
                            )
        print(page_attachments)
        return page_attachments

def get_page_comments(page_id):
    response = requests.get(f"{url}/rest/api/content/{page_id}/child/comment?expand=body.view&depth=all",
                             headers=headers, auth=(username, password))
    if response.status_code == 200:
        list_comments = response.json()['results']
        comments_text = []
        for comment in list_comments:
            comment_body = comment.get('body', {}).get('view', {}).get('value', '')
            if comment_body:
                # Parse the comment body with BeautifulSoup
                soup = BeautifulSoup(comment_body, 'html.parser')
                comment_text = soup.get_text()  # Extract text content
                comments_text.append(comment_text)
    
    return comments_text
        
def extract_urls_from_page_content(page_id, broken_links):
    content_url = f'{url}/rest/api/content/{page_id}?expand=body.view'
    response = requests.get(content_url, headers=headers, auth=(username, password))

    if response.status_code == 200:
        data = response.json()
        body_content = data['body']['view']['value']

        # Use regular expressions to find URLs in the body content
        page_urls = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+', body_content)
        if broken_links:
        # Filter and print URLs that start with 'https://inpixon.atlassian'
            broken_urls = []
            for page_url in page_urls:
                if page_url.startswith('https://inpixon.atlassian'):
                    broken_urls.append(page_url)
            return broken_urls
        if not broken_links:
            return page_urls
    else:
        print(f"Failed to retrieve page content: {response.status_code}")

# res = extract_urls_from_page_content(9306152, True)
# print(res)
# page_id = '7438376'
# commetns = get_page_comments(page_id)
# print(commetns)
# attachments = validate_attachements(page_id)
# print(attachments)
# e_urls = extract_urls_from_page_content(page_id, False)
# print(e_urls)
# 'Data Home':
# '7438346'
# 'IPS Architecture':
# '7438348'
# 'DATA COLLECTION ENGINE (DCE)':
# '7438352'