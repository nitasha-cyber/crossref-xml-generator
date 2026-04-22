from lxml import etree
from .base import BaseGenerator


class ReportGenerator(BaseGenerator):
    def add_to_body(self, body, data: dict):
        posted = etree.SubElement(body, "posted_content", type="report")
        if data.get("institution"):
            grp = etree.SubElement(posted, "institution")
            etree.SubElement(grp, "institution_name").text = data["institution"]
        self._add_common(posted, data)
        self._add_contributor(posted, data.get("author"), data.get("orcid"))
        self._add_pub_date(posted, data.get("publication_year"))
        if data.get("report_number"):
            etree.SubElement(posted, "item_number", item_number_type="report_number").text = data["report_number"]
        self._add_doi_data(posted, data["doi"])
