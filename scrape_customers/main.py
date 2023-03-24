import csv
from dataclasses import dataclass
from typing import List

import requests  # type: ignore
from bs4 import BeautifulSoup  # type: ignore


@dataclass
class Customer:
    customer_name: str
    logo_url: str


def scrape_pages(pages: list, output_file: str) -> None:
    page2function = {
        "https://scale.com": get_customers_scale,
        "https://deel.com": get_customers_deel,
        "https://webflow.com": get_customers_webflow,
    }
    with open(output_file, mode="w") as f:
        writer = csv.writer(f)
        writer.writerow(["Company", "Customer name", "Customer logo url"])

    for page in pages:
        content = requests.get(page)

        if content.status_code != 200:
            print(f"Unable to get page content from: {page}")
            continue

        soup = BeautifulSoup(content.content, "html.parser")

        if page in page2function:
            customers = page2function[page](soup)
            # Write customers to .csv file
            with open(output_file, mode="a+") as f:
                writer = csv.writer(f)
                for customer in customers:
                    writer.writerow([page, customer.customer_name, customer.logo_url])
        else:
            print(f"We don't have a function that can parse content of: {page}")


def get_customers_scale(soup: BeautifulSoup) -> List[Customer]:
    base_url = "https://scale.com/"
    scraped_customers = soup.find_all("img", {"class": "logo-grid_dark__2JTFY"})
    customers = [
        Customer(customer_name=c["alt"], logo_url=f"{base_url}{c['src']}")
        for c in scraped_customers
    ]
    return customers


def get_customers_deel(soup: BeautifulSoup) -> List[Customer]:
    div_before = soup.find("div", {"class": "header-sec"})
    div_selected = div_before.find_next_sibling("div")
    images = div_selected.find_all("img")
    customers = [Customer(c["alt"], c["src"]) for c in images]
    return customers


def get_customers_webflow(soup: BeautifulSoup) -> List[Customer]:
    div = soup.find("div", {"class": "intro-logos_wrapper"})
    images = div.find_all("img")
    customers = [Customer(c["alt"], c["src"]) for c in images]
    return customers


if __name__ == "__main__":
    pages_to_scrape = ["https://scale.com", "https://deel.com", "https://webflow.com"]
    scrape_pages(pages_to_scrape, "customers.csv")
