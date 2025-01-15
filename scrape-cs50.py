#####################################################################
# Script to Download cs50 using the week url
# Example url: https://cs50.harvard.edu/x/2025/weeks/0/
# Downloads most of the materials week by week in seperate folders
# Used procedural programming just wrote whatever thought in mind
# OOPS could have been better but lazy to even think rn
# Used:
# requests to download files from url
# shutil to copy file object
# time to wait for scroll
# pathlib to make folders n files
# selenium to parse html tree and navigate the web
# tqdm for download progress
######################################################################

import requests
import shutil
import time

from pathlib import Path
# import webdriver Options By
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.firefox.options import Options 
from tqdm.auto import tqdm

week_no: str
options = Options() 
options.add_argument("-headless") 

# replace spaces with '-' and everything lowercase
def convert_txt(txt: str):
    txt = txt.lower().split(" ")
    return "-".join(txt)

# scroll to element and click to reveal script code
def click_elem(driver, tag):
    # scroll element into view
    driver.execute_script("arguments[0].scrollIntoView();", tag)
    time.sleep(2)
    tag.click()

# Download File takes path, file name, download url and extension of file
def download_file(
    path: Path,
    file: str,
    url: str,
    extn: str
):
    file = Path(f"{file}-{week_no}.{extn}")

    # if file exists then dont download
    if path.joinpath(file).is_file():
        print(f"{file.name} already present...")
        return
    else:   # otherwise download file
        path.mkdir(parents=True, exist_ok=True)

        print(f"Downloading--------> {file.name}")
        # COPIED THIS PART from alpharithms even the comments sorry
        # make an HTTP request within a context manager
        with requests.get(url, stream=True) as res:
            
            # check header to get content length, in bytes
            total_length = int(res.headers.get("Content-Length"))
            
            # implement progress bar via tqdm
            with tqdm.wrapattr(res.raw, "read", total=total_length, desc="") as raw:
            
                # save the output to a file
                with open(f"./{path}/{file}", 'wb') as output:
                    shutil.copyfileobj(raw, output)
        print("\n")
# -----------------------------------------------------------------------------------------

# gettin lecture
def lecture_elems(
    lecture_ul: list,
    main_folder: str,
    driver
):
    lecture_path = Path(f"{main_folder}/lecture")
    for i in lecture_ul:
        # Notes url from lecture
        if i.find_element(By.TAG_NAME, "a").text == "Notes":
            notes_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
        
        # lecture slides urls google and pdf
        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Slides":
            slides_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            google_slides_url = slides_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")
            pdf_url = slides_ul[1].find_element(By.TAG_NAME, "a").get_attribute("href")
            # Download_file
            download_file(
                lecture_path.joinpath(i.find_elements(By.XPATH, "./span")[1].text.lower()),
                i.find_elements(By.XPATH, "./span")[1].text.lower(),
                pdf_url,
                "pdf"
            )
        
        # Source code from lecture indexed, pdf, zip
        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Source Code":
            source_code_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            source_code_index_url = source_code_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")
            source_code_pdf_url = source_code_ul[1].find_element(By.TAG_NAME, "a").get_attribute("href")
            source_code_zip_url = source_code_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                lecture_path.joinpath(convert_txt(i.find_elements(By.XPATH, "./span")[1].text)),
                convert_txt(i.find_elements(By.XPATH, "./span")[1].text),
                source_code_pdf_url,
                "pdf"
            )
            download_file(
                lecture_path.joinpath(convert_txt(i.find_elements(By.XPATH, "./span")[1].text)),
                convert_txt(i.find_elements(By.XPATH, "./span")[1].text),
                source_code_zip_url,
                "zip"
            )
        
        # Subtitles of lecture
        elif i.find_element(By.TAG_NAME, "a").text == "Subtitles":
            sub_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                lecture_path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                i.find_element(By.TAG_NAME, "a").text.lower(),
                sub_url,
                "srt"
            )
        
        # Transcript lecture
        elif i.find_element(By.TAG_NAME, "a").text == "Transcript":
            trans_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                lecture_path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                i.find_element(By.TAG_NAME, "a").text.lower(),
                trans_url,
                "txt"
            )
        
        # Lecture Video
        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Video":
            video_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            cs50_video_player_url = video_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")

            # clicking throught mp4--->hdr
            mp4_tag = video_ul[1].find_elements(By.XPATH, "./span")[0]
            click_elem(driver, mp4_tag)
            mp4_ul = video_ul[1].find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            hdr_tag = mp4_ul[0].find_elements(By.XPATH, "./span")[0]
            click_elem(driver, hdr_tag)

            # getting hdr_1080p video from hdr unordered list
            hdr_ul = mp4_ul[0].find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            hdr_1080_url = hdr_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            youtube_url = video_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                lecture_path.joinpath(i.find_elements(By.XPATH, "./span")[1].text.lower()),
                "lecture-"+i.find_elements(By.XPATH, "./span")[1].text.lower(),
                hdr_1080_url,
                "mp4"
            )
# --------------------------------------------------------------------------------------------------

# gettin shorts
def shorts_urls(shorts_ul: list):
    short_dict = {}
    for i in shorts_ul:
        short_dict.update({i.find_element(By.TAG_NAME, "a").text: i.find_element(By.TAG_NAME, "a").get_attribute("href")})
    return short_dict

def shorts_elems(short: dict, main_folder: str):
    count = 0
    for key, value in short.items():
        count += 1
        path = Path(f"{main_folder}/shorts/{count}-{convert_txt(key)}")
        start_short_driver(convert_txt(key), value, path)

def start_short_driver(title: str, url: str, path: Path):
    shorts_driver = webdriver.Firefox(options=options)
    shorts_driver.get(url)

    main_ul = shorts_driver.find_element(By.TAG_NAME, "main").find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
    for i in main_ul:
        if i.find_element(By.TAG_NAME, "a").text == "Slides":
            slides_pdf = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                title+"-"+i.find_element(By.TAG_NAME, "a").text.lower(),
                slides_pdf,
                "pdf"
            )
        elif i.find_element(By.TAG_NAME, "a").text == "Subtitles":
            subtitles_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                title+"-"+i.find_element(By.TAG_NAME, "a").text.lower(),
                subtitles_url,
                "pdf"
            )
        elif i.find_element(By.TAG_NAME, "a").text == "Transcript":
            transcript_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                title+"-"+i.find_element(By.TAG_NAME, "a").text.lower(),
                transcript_url,
                "pdf"
            )
        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Video":
            video_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            cs50_video_player_url = video_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")

            # clicking through mp4
            mp4_tag = video_ul[1].find_elements(By.XPATH, "./span")[0]
            click_elem(shorts_driver, mp4_tag)
            mp4_ul = video_ul[1].find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")

            # getting 1080p video from hdr unordered list
            p1080_url = mp4_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            youtube_url = video_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_elements(By.XPATH, "./span")[1].text.lower()),
                title+"-"+i.find_elements(By.XPATH, "./span")[1].text.lower(),
                p1080_url,
                "mp4"
            ) 
    shorts_driver.quit()
# --------------------------------------------------------------------------------------------------

# gettin section
def section_elems(url: str, main_folder: str):
    path = Path(f"{main_folder}/sections")

    sections_driver = webdriver.Firefox(options=options)
    sections_driver.get(url)

    main_ul = sections_driver.find_element(By.TAG_NAME, "main").find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
    for i in main_ul:
        if i.find_element(By.TAG_NAME, "a").text == "Audio":
            audio_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                "section"+"-"+i.find_element(By.TAG_NAME, "a").text.lower(),
                audio_url,
                "mp3"
            )

        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Slides":
            slides_pdf = i.find_element(By.TAG_NAME, "ul").find_element(By.TAG_NAME, "li").find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_elements(By.XPATH, "./span")[1].text.lower()),
                "section"+"-"+i.find_elements(By.XPATH, "./span")[1].text.lower(),
                slides_pdf,
                "pdf"
            )

        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Source Code":
            source_code_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            indexed_url = source_code_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")
            source_code_pdf = source_code_ul[1].find_element(By.TAG_NAME, "a").get_attribute("href")
            source_code_zip = source_code_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(convert_txt(i.find_elements(By.XPATH, "./span")[1].text)),
                convert_txt(i.find_elements(By.XPATH, "./span")[1].text)+"-"+"pdf",
                source_code_pdf,
                "pdf"
            )
            download_file(
                path.joinpath(convert_txt(i.find_elements(By.XPATH, "./span")[1].text)),
                convert_txt(i.find_elements(By.XPATH, "./span")[1].text)+"-"+"zip",
                source_code_zip,
                "zip"
            )

        elif i.find_element(By.TAG_NAME, "a").text == "Subtitles":
            subtitles_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                "section"+"-"+i.find_element(By.TAG_NAME, "a").text .lower(),
                subtitles_url,
                "srt"
            )

        elif i.find_element(By.TAG_NAME, "a").text == "Transcript":
            transcript_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_element(By.TAG_NAME, "a").text.lower()),
                "section"+"-"+i.find_element(By.TAG_NAME, "a").text .lower(),
                transcript_url,
                "txt"
            )

        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Video":
            video_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            cs50_video_player_url = video_ul[0].find_element(By.TAG_NAME, "a").get_attribute("href")

            # clicking through mp4
            mp4_tag = video_ul[1].find_elements(By.XPATH, "./span")[0]
            click_elem(sections_driver, mp4_tag)
            mp4_ul = video_ul[1].find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")

            # getting 1080p video from hdr unordered list
            p1080_url = mp4_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            youtube_url = video_ul[2].find_element(By.TAG_NAME, "a").get_attribute("href")
            download_file(
                path.joinpath(i.find_elements(By.XPATH, "./span")[1].text.lower()),
                "section"+"-"+i.find_elements(By.XPATH, "./span")[1].text.lower(),
                p1080_url,
                "mp4"
            )
    sections_driver.quit()
# ---------------------------------------------------------------------------------------------------------

def main():
    uri = input("Enter URL:")
    print("\n")
    driver = webdriver.Firefox(options=options)
    driver.get(uri)

    # main tag
    main_tag = driver.find_element(By.TAG_NAME, "main")
    # main tags
    heading = main_tag.find_element(By.TAG_NAME, "h1").text
    paragraph = main_tag.find_element(By.TAG_NAME, "p").text
    iframe = main_tag.find_element(By.TAG_NAME, "iframe")

    heading = heading.lower().split(" ")
    global week_no 
    week_no = heading[1]
    main_fldr = "-".join(heading)

    # main unordered list ---> list items list
    main_list = main_tag.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
    
    for i in main_list:
        # lecture unordered list ---> list items list
        if len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Lecture":
            lecture_ul = i.find_element(By.TAG_NAME, "ul").find_elements(By.XPATH, "./li")
            lecture_elems(
                lecture_ul,
                main_fldr,
                driver
            )

        # shorts unordered list ---> list items list
        elif len(i.find_elements(By.XPATH, "./span")) > 1 and i.find_elements(By.XPATH, "./span")[1].text == "Shorts":
            shorts_ul = i.find_element(By.TAG_NAME, "ol").find_elements(By.XPATH, "./li")
            short_dict = shorts_urls(shorts_ul)
            shorts_elems(
                short_dict,
                main_fldr
            )
        
        # section url ffurther parsing
        elif i.find_element(By.TAG_NAME, "a").text == "Section":
            section_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
            section_elems(section_url, main_fldr)

        # problem set url for further parsing maybe
        elif "Problem Set" in i.find_element(By.TAG_NAME, "a").text:
            prbm_set_url = i.find_element(By.TAG_NAME, "a").get_attribute("href")
    driver.quit()

if __name__ == "__main__":
    main()