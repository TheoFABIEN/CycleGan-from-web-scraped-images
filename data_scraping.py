import bs4 
from selenium import webdriver 
import os 
import time
import matplotlib.pyplot as plt 
from selenium.webdriver.common.by import By
import requests
import io
from PIL import Image
from pathlib import Path

#%%


def scroll_down_page(driver):
    driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    time.sleep(.5)

#%%


driver = webdriver.Firefox()


def launch_page(url, class_name):
    driver.get(url)
    html = driver.page_source
    soup = bs4.BeautifulSoup(html, 'html.parser')

    containers = soup.findAll('div', {'class': class_name})
    num_containers = len(containers)
    print(f"I found {num_containers} containers.")

    return soup, containers, num_containers



#%%

def find_full_resolution_urls(max_images, thumbnails_class_name, full_img_xpath):
    """
    Click on images thumbnails and access the urls of the 
    full resolution images.
    """
            
    img_urls = set()
    skips = 0

    while len(img_urls) + skips < max_images:

        scroll_down_page(driver)

        elements = driver.find_elements(
                By.CLASS_NAME,
                thumbnails_class_name
        )

        for image in elements[len(img_urls) + skips:max_images]:
            try:
                image.click()
                time.sleep(.1)
                image_url = image.get_attribute('src')
            except:
                print('Exception')
                continue
            full_imgs = driver.find_elements(
                    By.XPATH,
                    full_img_xpath
            )
            for full_img in full_imgs:
                if full_img.get_attribute('src') in img_urls:
                    max_images += 1 
                    skips += 1
                    break
                if full_img.get_attribute('src') and 'http' in full_img.get_attribute('src'):
                    print(full_img.get_attribute('src'))
                    img_urls.add(full_img.get_attribute('src'))

    return img_urls
    
#%%

def download_image(output_folder, img_name, url):
    
    try:
        img_data = requests.get(url).content
        img_file = io.BytesIO(img_data)
        image = Image.open(img_file)
        file_path = Path(output_folder + "/" + img_name)

        with open(file_path, 'wb') as f:
            image.save(f, "JPEG")

        print("Image saved.")

    except Exception as e:
        print(f'Failed: {e}')




#%%  Now apply all these functions to scrape our data

# Here are the urls we will be using
anime_search_1 = 'https://www.google.com/search?q=anime+natural+landscape&sca_esv=dc10ca3b9a9df2ee&sca_upv=1&udm=2&biw=1920&bih=520&ei=R6ruZoT8CaedkdUPkv3riAQ&ved=0ahUKEwjEu_Ht89OIAxWnTqQEHZL-GkEQ4dUDCBA&uact=5&oq=anime+natural+landscape&gs_lp=Egxnd3Mtd2l6LXNlcnAiF2FuaW1lIG5hdHVyYWwgbGFuZHNjYXBlSIMNULkFWI8McAF4AJABAJgBOKABlAOqAQE4uAEDyAEA-AEBmAIFoALXAcICChAAGIAEGEMYigXCAgUQABiABMICBhAAGAcYHsICCBAAGAcYCBgemAMAiAYBkgcBNaAH6BY&sclient=gws-wiz-serp'

photo_search_1 = "https://www.google.com/search?sca_esv=dc10ca3b9a9df2ee&sca_upv=1&q=nature+landscape+photography+photos&uds=ADvngMjcH0KdF7qGWtwTBrP0nt7d2Rv61oHjFtTQfJwmu1EntCnTXkhsNnF7ZhGTU6qK-kCcJ-7N9nkUP5fbDpjYIRxnt7tfA7Fi6-cMNGvrVem2GsVskLiX6tmoJHqZDkc24YuSlifoWFx0IrwNy70vo6V-21MlSU7pK6yM41h4Yp21qU1JjP8&udm=2&sa=X&ved=2ahUKEwiPvaOvpdaIAxWfVaQEHXrAE10QxKsJegQICxAB&ictx=0&biw=958&bih=918&dpr=1"

anime_search_2 = "https://www.google.com/search?sca_esv=dc10ca3b9a9df2ee&sca_upv=1&q=anime+city+scenery&uds=ADvngMjcH0KdF7qGWtwTBrP0nt7dEPozNF4nTr3IUmxjgNKk04D_ZJsc8vmoFFIj6i4c4EFQmNbSfNftLEzov-QKOSZyv9__AH5m0smiy1CJ_i0slFH-ifQlT4arVFKK1ovZ4N3CW2U_sqI669Aq5_e_ip4MAuA-xA&udm=2&sa=X&ved=2ahUKEwiKqZGJ-taIAxWpcKQEHfn3CLkQxKsJegUIiwEQAQ&ictx=0&biw=1280&bih=843&dpr=1"

photo_search_2 = "https://www.google.com/search?q=town+photography&sca_esv=dc10ca3b9a9df2ee&sca_upv=1&udm=2&biw=958&bih=946&ei=L0bwZrvhJcTOhbIP4PiXcA&oq=town+photo&gs_lp=Egxnd3Mtd2l6LXNlcnAiCnRvd24gcGhvdG8qAggBMgUQABiABDIEEAAYHjIEEAAYHjIEEAAYHjIGEAAYBRgeMgYQABgFGB4yBhAAGAUYHjIGEAAYBRgeMgYQABgFGB4yBhAAGAUYHkjhHlD5A1jgFHADeACQAQCYAT6gAYwEqgECMTK4AQPIAQD4AQGYAgygAuADwgIKEAAYgAQYQxiKBcICBhAAGAcYHsICCBAAGIAEGLEDwgINEAAYgAQYsQMYQxiKBcICCxAAGIAEGLEDGIMBmAMAiAYBkgcCMTKgB8M0&sclient=gws-wiz-serp"


DESTINATION_FOLDER = 'D:\ML_Projects\CycleGan\Test_dataset' 
MAX_IMAGES = 500

#%% Main loop through the 4 pages to scrape all images

for i, url in enumerate([anime_search_1, anime_search_2, photo_search_1, photo_search_2]):

    # xpath of the full resolution image can change depending on the page
    if i == 0:
        full_img_xpath = "/html/body/div[6]/div/div/div/div/div/div/c-wiz/div/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]"
    elif i == 1:
        full_img_xpath = "/html/body/div[5]/div/div/div/div/div/div/c-wiz/div/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]"
    elif i == 2:
        full_img_xpath = "/html/body/div[5]/div/div/div/div/div/div/c-wiz/div/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]"
    else:
        full_img_xpath = "/html/body/div[5]/div/div/div/div/div/div/c-wiz/div/div[2]/div[2]/div/div[2]/c-wiz/div/div[3]/div[1]/a/img[1]"

    subfolder = "\Anime" if i == 0 or i == 1 else "\Photos"
    subs = "1_" if i == 0 or i == 2 else "2_" # Avoid overlapping names when saving 

    soup, containers, num_containers = launch_page(
            url,
            "eA0Zlc WghbWd FnEtTd mkpRId m3LIae RLdvSe qyKxnc ivg-i PZPZlf GMCzAd"
    )

    time.sleep(1)

    img_urls = find_full_resolution_urls(
            max_images = MAX_IMAGES,
            thumbnails_class_name = "H8Rx8c",
            full_img_xpath = full_img_xpath
    )

    # Download the images 
    for i, img_url in enumerate(img_urls):
        download_image(
                DESTINATION_FOLDER + subfolder,
                subs + str(i) + ".jpg",
                img_url
        )


##%%
