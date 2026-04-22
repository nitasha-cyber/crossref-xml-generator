from lxml import etree
from .base import BaseGenerator


class ProceedingGenerator(BaseGenerator):
    def add_to_body(self, body, data: dict):
        conference = etree.SubElement(body, "conference")
        if data.get("conference_name"):
            event = etree.SubElement(conference, "event_metadata")
            etree.SubElement(event, "conference_name").text = data["conference_name"]
            if data.get("conference_location"):
                etree.SubElement(event, "conference_location").text = data["conference_location"]

        paper = etree.SubElement(conference, "conference_paper")
        self._add_common(paper, data)
        self._add_contributor(paper, data.get("author"), data.get("orcid"))
        self._add_pub_date(paper, data.get("publication_year"))
        self._add_doi_data(paper, data["doi"])
