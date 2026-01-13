from python.scripts.scrapper import scrape
from python.scripts.preprocess import preprocess
from python.scripts.prepare import prepare


def main():
    scrape()
    preprocess()
    prepare()


if __name__ == "__main__":
    main()
