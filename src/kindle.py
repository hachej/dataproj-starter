from webbot import Browser
from datetime import datetime 
import time 

URL = "https://read.amazon.com/notebook?ref_=kcr_notebook_lib&language=en-US"
KINDLE_USR = "julien.hurault@gmail.com"
KINDLE_PWD = "><ij9C-6(sdf"

class Kindle:
    def __init__(self):
        self.web = Browser()
        self.login()
        time.sleep(1)
        
    def get_creds(self):
        username = KINDLE_USR
        password = KINDLE_PWD
        return username, password

    def login(self):
        self.web.go_to(URL)
        username, password = self.get_creds()
        self.web.type(username, id='ap_mail')
        self.web.type(password, id='ap_password')
        self.web.press(self.web.Key.ENTER)

    def extract_books(self):
        h2s = self.web.find_elements(tag='h2')
        books = []
        for h in h2s:
            books.append(h)
        return books

    def extract_highlights(self, book_element):
        book_element.click()
        time.sleep(2)
        elements = self.web.find_elements(id='highlight')
        highlights = []
        for e in elements:
            highlights.append(e.text)
        return highlights

    def extract_meta_kindle(self, book_element):
        book_element.click()
        elements = self.web.find_elements(id='kp-notebook-annotated-date')

        if len(elements) != 1:
            time.sleep(3)
            elements = self.web.find_elements(id='kp-notebook-annotated-date')

        last_update_date = datetime.strptime(elements[0].text, '%A %B %d, %Y')
        elements = self.web.find_elements(id='kp-notebook-highlights-count')
        
        if len(elements) > 0:
            n_highlights = int(elements[0].text)
            not_displayable = self.web.find_elements("Sorry, we’re unable to display this type of content.")
            n_highlights -= len(not_displayable)
        else:
            n_highlights = None

        return last_update_date, n_highlights

