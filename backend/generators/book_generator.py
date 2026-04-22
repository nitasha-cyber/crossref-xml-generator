from lxml import etree
from .base import BaseGenerator


class BookGenerator(BaseGenerator):
    def add_to_body(self, body, data: dict):
        book = etree.SubElement(body, "book", book_type="monograph")
        book_meta = etree.SubElement(book, "book_metadata")
        self._add_common(book_meta, data)
        self._add_contributor(book_meta, data.get("author"), data.get("orcid"))
        self._add_pub_date(book_meta, data.get("publication_year"))
        if data.get("isbn"):
            etree.SubElement(book_meta, "isbn").text = data["isbn"]
        if data.get("publisher"):
            publisher = etree.SubElement(book_meta, "publisher")
            etree.SubElement(publisher, "publisher_name").text = data["publisher"]
        self._add_doi_data(book_meta, data["doi"])
