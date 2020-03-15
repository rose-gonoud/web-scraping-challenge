# Dependencies
from bs4 import BeautifulSoup as bs
import pandas as pd
from splinter import Browser
import requests
import time
import pymongo

def scrape():
    # go to the NASA Mars News site
    nasa_mars_news="https://mars.nasa.gov/news/?page=0&per_page=40&order=publish_date+desc%2Ccreated_at+desc&search=&category=19%2C165%2C184%2C204&blank_scope=Latest"
    response = requests.get(nasa_mars_news)
    # Create a BeautifulSoup object; parse with 'html.parser'
    soup1 = bs(response.text, 'html.parser')
    # collect latest news title and preview blurb
    news_title = soup1.find(class_="content_title").a.text.strip()
    news_p = soup1.find(class_="rollover_description_inner").text.strip()
    # this tells python (through Splinter) to control chrome
    executable_path = {'executable_path': '/usr/local/bin/chromedriver'}
    browser = Browser('chrome', **executable_path, headless=False)


    # go to the Jet Propulsion Lab page
    url = 'https://www.jpl.nasa.gov/spaceimages/?search=&category=Mars'
    browser.visit(url)
    browser.links.find_by_partial_text('FULL').click()
    time.sleep(4)
    # navigate from featured image full screen
    browser.links.find_by_partial_href('spaceimages/details').click()
    # search for the URL by looking into the HTML
    new_html = browser.html
    soup3 = bs(new_html, "html.parser")
    img_tag = soup3.find('figure', class_='lede').a
    # grab the URL for the full featured image
    featured_image_url = f"https://www.jpl.nasa.gov{img_tag['href']}"


    # go to the NASA twitter page
    # Comments in bottom of this block from a selenium solution for filtering weather-only tweets and selecting one:
    # I was told my selector was invalid or illegal, I'm guessing the second one. Might have worked otherwise.
    # Source:
    # (https://medium.com/analytics-vidhya/create-your-own-twitter-dataset-with-this-simple-python-scraper-710bf7c5dc04)

    # browser=webdriver.Chrome()
    twitter_url="https://twitter.com/marswxreport?lang=en"
    browser.visit(twitter_url)
    time.sleep(4)
    html = browser.html
    soup4 = bs(html, 'html.parser')
    # retrieval of generic tag
    mars_weather = soup4.find('article').text.strip()
    # mars_weather=[]
    # for result in browser.find_elements_by_class_name("^css-1dbjc4n"):
    #       try:
    #         text = browser.find_by_partial_text("InSight sol")
        
    #           if text:
    #             mars_weather.append(text)
            
    #         else: print("if nope!")
            
    #     except: print("try nope!")


    # go to the space-facts site
    facts_url="https://space-facts.com/mars/"
    # scrape the table in to a pandas HTML reader
    mars_facts = pd.read_html(facts_url)
    # limit result to only the first list item (a DF) that contains the mars specific stuff
    mars_facts = mars_facts[0]
    # rename columns easy names to be called during the dict conversion
    mars_facts = mars_facts.rename(columns={0: "Description", 1: "Value"})
    # perform list-to-dictionary conversion
    mars_facts_dict = mars_facts.set_index('Description')['Value'].to_dict()



    # go to the USGS Mars hemispheres page
    hemispheres_url='https://astrogeology.usgs.gov/search/results?q=hemisphere+enhanced&k1=target&v1=Mars'
    browser.visit(hemispheres_url)
    # look at the HTML for the hemispheres page
    new_html=browser.html
    soup5 = bs(new_html, "html.parser")
    # retrieve the parent divs containing all hemisphere photos
    results = soup5.find_all('div', class_='item')

    # extract just the photo header text from each hemisphere
    headers = []
    for result in results:
        # scrape the hemisphere photo titles
        title = result.find('h3').text
        headers.append(title)
        
    # extract just the hemisphere names from the header text
    hemispheres = []
    for header in headers:
        hemi_name = header.split(' ')[0]
        hemispheres.append(hemi_name)

    # write a simple lowercasing function
    def first_lower(s):
        if len(s) == 0:
            return s
        else:
            return s[0].lower() + s[1:]

    # make all extracted hemisphere names lowercased w/ above fn, to prep for URL insertion (case sensitive)
    url_hemi_names = []
    for hemisphere in hemispheres:
        lowercased = first_lower(hemisphere)
        url_hemi_names.append(lowercased)

    # use lowercased hemisphere names to loop thru each hemisphere page and extract the full image url from each
    img_urls=[]
    for name in url_hemi_names:
        browser.visit(hemispheres_url)
        current = browser.links.find_by_partial_href(f'Viking/{name}')['href']
        browser.visit(current)

        url = browser.find_by_text('Sample')['href']
        img_urls.append(url)
        
    # save all hemisphere info in a dictionary
    hemisphere_image_urls = [
        {"title": headers[0], "img_url": img_urls[0]},
        {"title": headers[1], "img_url": img_urls[1]},
        {"title": headers[2], "img_url": img_urls[2]},
        {"title": headers[3], "img_url": img_urls[3]},   
    ]

    # write all scraping results to one master dictionary
    master_dict = {
    "collection_timestamp":time.time(),    
    "news_title":news_title,
    "news_p":news_p,
    "featured_image_url":featured_image_url,
    "mars_weather":mars_weather,
    "mars_facts":mars_facts_dict,
    "hemisphere_info":hemisphere_image_urls
    }

    return master_dict