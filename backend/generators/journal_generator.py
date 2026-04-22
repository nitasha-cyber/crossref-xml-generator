from lxml import etree
from .base import BaseGenerator


class JournalGenerator(BaseGenerator):
    def add_to_body(self, body, data: dict):
        journal = etree.SubElement(body, "journal")
        journal_meta = etree.SubElement(journal, "journal_metadata")
        etree.SubElement(journal_meta, "full_title").text = data.get("journal_title") or "Journal"
        if data.get("issn"):
            etree.SubElement(journal_meta, "issn", media_type="electronic").text = data["issn"]

        issue = etree.SubElement(journal, "journal_issue")
        self._add_pub_date(issue, data.get("publication_year"))
        if data.get("volume"):
            vol = etree.SubElement(issue, "journal_volume")
            etree.SubElement(vol, "volume").text = data["volume"]
        if data.get("issue"):
            etree.SubElement(issue, "issue").text = data["issue"]

        article = etree.SubElement(journal, "journal_article", publication_type="full_text")
        self._add_common(article, data)
        self._add_contributor(article, data.get("author"), data.get("orcid"))
        if data.get("first_page") or data.get("last_page"):
            pages = etree.SubElement(article, "pages")
            if data.get("first_page"):
                etree.SubElement(pages, "first_page").text = data["first_page"]
            if data.get("last_page"):
                etree.SubElement(pages, "last_page").text = data["last_page"]
        self._add_doi_data(article, data["doi"])
