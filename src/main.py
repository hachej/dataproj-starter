from webbot import Browser

URL = "https://read.amazon.com/notebook?ref_=kcr_notebook_lib&language=en-US"

def get_creds():
    username = "julien.hurault@gmail.com"
    password = "><ij9C-6(sdf"
    return username, password
def login(web):
    web.go_to(URL)
    username, password = get_creds()
    web.type(username, id='ap_mail')
    web.type(password, id='ap_password')
    web.press(web.Key.ENTER)

def extractBooks(web):
    h2s = web.find_elements(tag='h2')
    books = []
    for h in h2s:
        books.append(h.text)
    return books

web = Browser()
login(web)