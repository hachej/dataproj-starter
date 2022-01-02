from src.kindle import Kindle
from src.notion import Notion
import logging 
import sys

# TO DO :
# add cron
# load env from file 

HIGHLIGHT_DB_ID = '2fe03b1165f643a798e75a5eaa9302d5'
BOOK_DB_ID = 'b93781d4aa774e6f9029740aca154f6a'

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.StreamHandler(sys.stdout))

notion = Notion()

def query_notion_highlights(books_notion_id):
    filter = {
    "filter": {
        "property": "Book",
            "relation": {
                "contains": books_notion_id
            }
            }
    }
    highlights = notion.query(HIGHLIGHT_DB_ID, filter)
    highlights = [b["properties"]["Name"]["title"][0]["text"]["content"] for b in highlights]
    return  highlights

def query_notion_books():
    filter = {}
    books = notion.query(BOOK_DB_ID, filter)
    books_notion_names = [b["properties"]["Name"]["title"][0]["text"]["content"] for b in books]
    books_notion_ids = [b["id"] for b in books]
    return  books_notion_names, books_notion_ids

def insert_book(book, n_highlights, date):
    properties =  {
            'Name': {
                    'type': 'title',
                    'title': [{'type': 'text',
                        'text': {'content': book, 'link': None},
                        'plain_text': book}
                        ]
                    },
            'Date': {
                'type': 'date',
                'date': {'start': date.strftime("%Y-%m-%d"), 'end': None, 'time_zone': None}
            },
            'highlights': {'type': 'number', 'number': n_highlights},
        }
    book_id = notion.insert(BOOK_DB_ID, properties)
    return book_id

def insert_highlight(highlight, book_id):
    properties =  {
        'Book': {
                'type': 'relation',
                'relation': [{'id': book_id}]},
        'Name': {'id': 'title',
                'type': 'title',
                'title': [{'type': 'text',
                    'text': {'content': highlight, 'link': None},
                    'plain_text': highlight}
                    ]
                }
        }
    notion.insert(HIGHLIGHT_DB_ID, properties)

if __name__ == '__main__':
    logger.info("### start ###")
    kindle = Kindle()
    books_kindle = kindle.extract_books()
    logger.info(f"#{len(books_kindle)} books found in Kindle")

    # get notion books
    books_notion_names, books_notion_ids = query_notion_books()

    # Loop over kindle books
    for book_element in books_kindle:
        book_name = book_element.text
        logger.info(f"#[{book_name}]: Start")
        last_update_date, n_highlights = kindle.extract_meta_kindle(book_element)

        # if book not in book db -> we insert it
        if book_name not in books_notion_names:
            logger.info(f"#[{book_name}]: Create book in Notion book DB")
            books_notion_id = insert_book(book_name, n_highlights, last_update_date)
        else:
            books_notion_id = books_notion_ids[books_notion_names.index(book_name)]
        
        # we load the highlights for this book in Notion
        highlights_notion = query_notion_highlights(books_notion_id)

        # if number of highlights differs between kindle and notion we load the delta
        if len(highlights_notion) != n_highlights:
            logger.info(f"#[{book_name}]: Loading {n_highlights-len(highlights_notion)} highlights for book {book_name}")
            highlights_amazon = kindle.extract_highlights(book_element)
            
            # check if error in the load of kindle highlights
            if len(highlights_amazon) != n_highlights:
                print("error", len(highlights_amazon), n_highlights)
                raise 
            
            # load only the highlights not present in Notion
            for h_amz in highlights_amazon:
                if h_amz not in highlights_notion and h_amz != 'Hello,Julien':
                    insert_highlight(h_amz[:2000],books_notion_id)
        else:
            logger.info(f"#[{book_name}]: Nothing to load")