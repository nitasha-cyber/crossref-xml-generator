from lxml import etree
from .base import BaseGenerator


class PostedContentGenerator(BaseGenerator):
    def add_to_body(self, body, data: dict):
        posted = etree.SubElement(body, "posted_content", type=data.get("posted_content_type") or "preprint")
        if data.get("institution"):
            grp = etree.SubElement(posted, "institution")
            etree.SubElement(grp, "institution_name").text = data["institution"]
        self._add_common(posted, data)
        self._add_contributor(posted, data.get("author"), data.get("orcid"))
        self._add_pub_date(posted, data.get("publication_year"))
        self._add_doi_data(posted, data["doi"])
