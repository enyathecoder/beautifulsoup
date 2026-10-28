import sys
from bs4 import BeautifulSoup, SoupStrainer


def main():
    if len(sys.argv) < 2:
        print("Usage: python task2.py <html_file>")
        sys.exit(1)

    html_file = sys.argv[1]

    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Only parse <a> tags that have an href attribute, ignore others.
        only_parts = SoupStrainer('a', href=True)
        soup = BeautifulSoup(html_content, 'lxml', parse_only=only_parts)

        for link in soup.find_all('a', href=True):
            print(link.get('href'))

    except FileNotFoundError:
        print(f"Error: The file '{html_file}' was not found.")
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()