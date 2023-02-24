import json
import os
import time
import pytube
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.common import TimeoutException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scroll_to_bottom import scroll_to_bottom

username = "ben.limitedvision@gmail.com"
password = "Aenima_11667801475"

driver = webdriver.Chrome("chromedriver")
driver.fullscreen_window()
driver.get("https://edu.genius.space/ru/login")

timeout = 5

try:
    element_present = EC.presence_of_element_located(("css selector", "input[type='email']"))
    WebDriverWait(driver, timeout).until(element_present)
except TimeoutException:
    pass

driver.find_element("css selector", "input[type='email']").send_keys(username)
driver.find_element("css selector", "input[type='password']").send_keys(password)

driver.find_element("css selector", ".main-button").click()

WebDriverWait(driver, 5).until(EC.presence_of_element_located(("css selector", ".courses-item")))

time.sleep(3)
loadMoreBTN = ''
while True:
    scroll_to_bottom(driver)
    time.sleep(1)
    loadMoreBTN = driver.find_element("css selector", ".btn__load-more")
    try:
        loadMoreBTN.click()
        time.sleep(3)
        print()
    except:
        break

coursesURLList = []

coursesList = []

for course in driver.find_elements("css selector", ".courses-item"):
    coursesURLList.append(course.find_element("css selector", "a.courses-item__name").get_attribute("href"))

for courseURL in coursesURLList:
    driver.get(courseURL)
    time.sleep(4)
    isVimeo = False
    source = driver.page_source

    soup = BeautifulSoup(source, 'html.parser')
    courseTitle = soup.find('div', {'class': 'courses-dashboard_head-desc'}).find('h1').text.strip()
    print(courseTitle)
    courseDescription = soup.find('div', {'class': 'courses-dashboard_desc-content'}).text

    lessonsList = []
    modulesWrapper = soup.find('div', {'class': 'courses-dashboard_modules__wrap'})
    modulesBlocks = modulesWrapper.find_all('div', {'class': 'courses-dashboard_modules-item'})

    for module in modulesBlocks:
        lessonsDivs = module.find_all('li')
        for lessonDiv in lessonsDivs:
            lessonTitle = lessonDiv.find('div', {'class': 'courses-dashboard_lesson-name'}).text.strip()
            lessonDescription = lessonDiv.find('div', {'class': 'courses-dashboard_lesson-desc'}).text.strip()
            lessonURL = lessonDiv.find('a', {'class': 'courses-dashboard_lesson-wrap'})['href']

            driver.get('https://edu.genius.space' + lessonURL)
            time.sleep(3)
            lessonSource = driver.page_source
            lessonSoup = BeautifulSoup(lessonSource, 'html.parser')
            lessonVideoURL = ''
            try:
                lessonVideoURL = lessonSoup.find('div', {'class': 'plyr__video-wrapper'}).find('iframe')['src']
            except:
                pass
            if 'vimeo.com' in lessonVideoURL:
                isVimeo = True
                break
            lessonDocumentsDivList = lessonSoup.find_all('a', {'class': 'additional-materials__download'})
            lessonDocumentsURLsList = []

            for lessonDocument in lessonDocumentsDivList:
                lessonDocumentsURLsList.append(lessonDocument['href'])

            outputString = f'{lessonTitle} \n {lessonDescription} \n video: {lessonVideoURL} \n documents: {lessonDocumentsURLsList}'

            lessonDict = {'lessonTitle': lessonTitle.replace(':', ' ').replace('|', ' ').replace('?', ' '),
                          'lessonDescription': lessonDescription,
                          'lessonVideoURL': lessonVideoURL,
                          'lessonFilesList': lessonDocumentsURLsList}

            lessonsList.append(lessonDict)
        if isVimeo:
            break
    if isVimeo:
        continue
    courseDict = {'courseTitle': courseTitle.replace(':', ' ').replace('|', ' ').replace('?', ' '),
                  'courseDescription': courseDescription,
                  'courseLessons': lessonsList}

    coursesList.append(courseDict)

    print("course " + courseTitle + " done")
for course in coursesList:
    print(course)

courseCounter = 1
os.makedirs('courses')
for course in coursesList:
    courseSavePathName = f'courses/{courseCounter}. {course["courseTitle"]}'
    os.makedirs(courseSavePathName)
    lessonsCounter = 1
    for lesson in course['courseLessons']:
        lessonSavePathName = courseSavePathName + f'/{lessonsCounter}'

        lessonYoutubeURL = lesson['lessonVideoURL'].split('?')[0].replace('embed/', 'watch?v=')
        print(lessonYoutubeURL)

        os.makedirs(lessonSavePathName)
        with open(lessonSavePathName + '/Info.txt', "a", encoding="utf-8") as file:
            file.write(f'{lesson["lessonTitle"]} \n\n'
                       f'Document links \n')
            for lessonFile in lesson['lessonFilesList']:
                file.write(lessonFile + '\n')
        if lesson['lessonVideoURL']:
            try:
                youtube = pytube.YouTube(lessonYoutubeURL)
                video = youtube.streams.filter(progressive=True, file_extension="mp4").get_highest_resolution()
                video.download(lessonSavePathName)
            except:
                pass

        lessonsCounter = lessonsCounter + 1

    courseCounter = courseCounter + 1
