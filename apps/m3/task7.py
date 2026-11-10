import sys
from bs4 import BeautifulSoup, SoupReplacer


def add_test_class(tag):
    if tag.name == "p":
        return {**tag.attrs, "class": "test"}
    return None


def main():
    if len(sys.argv) < 2:
        print("Usage: python task7.py <html_file>")
        sys.exit(1)

    html_file = sys.argv[1]

    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

        # Add class="test" to every <p> *during* parsing.
        # No second pass over the tree is needed.
        p_class_test = SoupReplacer(attrs_xformer=add_test_class)
        soup = BeautifulSoup(html_content, 'lxml', replacer=p_class_test)

        output_path = "output_task7.html"
        with open(output_path, 'w', encoding='utf-8') as output_file:
            output_file.write(soup.prettify())
        print(f"Modified HTML has been written to {output_path}")

    except FileNotFoundError:
        print(f"Error: The file '{html_file}' was not found.")
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()