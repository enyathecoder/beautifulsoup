import sys
from collections import Counter

from bs4 import BeautifulSoup

def main():
    if len(sys.argv) < 2:
        print("Usage: python iterate.py <html_file>")
        sys.exit(1)

    html_file = sys.argv[1]

    try:
        with open(html_file, 'r', encoding='utf-8') as file:
            html_content = file.read()

        soup = BeautifulSoup(html_content, 'html.parser')

        # Walk every node of the tree with a plain for loop.
        counts = Counter()
        for number, node in enumerate(soup):
            counts[type(node).__name__] += 1
            if number < 10:  # show the first few nodes only
                label = node.name if node.name else repr(str(node)[:40])
                print(f"{number:>3}  {type(node).__name__:<15} {label}")

        print()
        print("Node types:")
        for kind, count in counts.most_common():
            print(f"  {kind:<15} {count}")
        print(f"  {'total':<15} {sum(counts.values())}")

    except FileNotFoundError:
        print(f"Error: The file '{html_file}' was not found.")
        sys.exit(1)

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()