from datetime import datetime, timezone
from lxml import etree

from config import CROSSREF_BATCH_ID_PREFIX, DEPOSITOR_EMAIL, DEPOSITOR_NAME, REGISTRANT

XSI_NS = "http://www.w3.org/2001/XMLSchema-instance"
JATS_NS = "http://www.ncbi.nlm.nih.gov/JATS1"
AI_NS = "http://www.crossref.org/AccessIndicators.xsd"


class BaseGenerator:
    @staticmethod
    def create_root():
        timestamp = datetime.now(timezone.utc).strftime("%Y%m%d%H%M%S")
        root = etree.Element(
            "doi_batch",
            version="5.3.1",
            nsmap={
                None: "http://www.crossref.org/schema/5.3.1",
                "xsi": XSI_NS,
                "jats": JATS_NS,
                "ai": AI_NS,
            },
        )
        root.set(
            etree.QName(XSI_NS, "schemaLocation"),
            "http://www.crossref.org/schema/5.3.1 https://data.crossref.org/schemas/crossref5.3.1.xsd",
        )

        head = etree.SubElement(root, "head")
        etree.SubElement(head, "doi_batch_id").text = f"{CROSSREF_BATCH_ID_PREFIX}-{timestamp}"
        etree.SubElement(head, "timestamp").text = timestamp
        depositor = etree.SubElement(head, "depositor")
        etree.SubElement(depositor, "depositor_name").text = DEPOSITOR_NAME
        etree.SubElement(depositor, "email_address").text = DEPOSITOR_EMAIL
        etree.SubElement(head, "registrant").text = REGISTRANT

        body = etree.SubElement(root, "body")
        return root, body

    @staticmethod
    def _add_contributor(parent, author: str | None, orcid: str | None = None):
        if not author:
            return
        contributors = etree.SubElement(parent, "contributors")
        person = etree.SubElement(contributors, "person_name", contributor_role="author", sequence="first")
        etree.SubElement(person, "given_name").text = author
        if orcid:
            etree.SubElement(person, "ORCID").text = orcid

    @staticmethod
    def _add_common(parent, data: dict):
        titles = etree.SubElement(parent, "titles")
        etree.SubElement(titles, "title").text = data.get("title", "")

        if data.get("abstract"):
            etree.SubElement(parent, etree.QName(JATS_NS, "abstract")).text = data["abstract"]

        if data.get("license_url"):
            program = etree.SubElement(parent, etree.QName(AI_NS, "program"), name="AccessIndicators")
            license_ref = etree.SubElement(program, etree.QName(AI_NS, "license_ref"))
            license_ref.text = data["license_url"]

    @staticmethod
    def _add_pub_date(parent, year: int | str):
        pub = etree.SubElement(parent, "publication_date", media_type="online")
        etree.SubElement(pub, "year").text = str(year)

    @staticmethod
    def _add_doi_data(parent, doi: str):
        doi_data = etree.SubElement(parent, "doi_data")
        etree.SubElement(doi_data, "doi").text = doi
        etree.SubElement(doi_data, "resource").text = f"https://doi.org/{doi}"

    @staticmethod
    def to_xml_bytes(root):
        return etree.tostring(root, pretty_print=True, xml_declaration=True, encoding="UTF-8")
