import sys
from bs4 import BeautifulSoup, SoupStrainer

def main():
    if len(sys.argv) < 2:
        print("Usage: python task4.py <html_file>")
        sys.exit(1)

    html_file = sys.argv[1]

    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Only parse tags that have an id attribute
        only_parts = SoupStrainer(id=True)
        soup = BeautifulSoup(html_content, 'lxml', parse_only=only_parts)

        for tag in soup.find_all(id=True):
            print(tag)

    except FileNotFoundError:
        print(f"Error: The file '{html_file}' was not found.")
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()