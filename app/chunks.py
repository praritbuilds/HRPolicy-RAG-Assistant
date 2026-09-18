import json
import re

from pypdf import PdfReader


PDF_PATH = "data/employee-handbook.pdf"
OUTPUT_PATH = "data/policy_chunks.json"

START_PDF_PAGE = 5
PAGE_OFFSET = 4


SECTION_PATTERN = re.compile(
    r"^(I{1,3}|IV|V)\.\s+.+"
)

SUBSECTION_PATTERN = re.compile(
    r"^[A-Z]\.\s+.+"
)

GROUP_PATTERN = re.compile(
    r"^\d+\.\s+.+"
)

POLICY_PATTERN = re.compile(
    r"^[a-z]\.\s+.+"
)


def remove_footer_page_number(text, printed_page):
    if printed_page is None:
        return text.strip()

    cleaned_lines = []

    for line in text.splitlines():
        # Remove only a line that contains exactly
        # the expected printed page number.
        if line.strip() == str(printed_page):
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines).strip()


def extract_pages(file_path):
    reader = PdfReader(file_path)

    pages = []

    for pdf_page, page in enumerate(
        reader.pages,
        start=1
    ):
        if pdf_page < START_PDF_PAGE:
            continue

        text = page.extract_text()

        if not text:
            continue

        printed_page = (
            pdf_page - PAGE_OFFSET
        )

        text = remove_footer_page_number(
            text,
            printed_page
        )

        pages.append({
            "pdf_page": pdf_page,
            "printed_page": printed_page,
            "text": text
        })

    return pages


def parse_policy_line(line):
    if ":" not in line:
        return line.strip(), ""

    heading, content = line.split(
        ":",
        1
    )

    return (
        heading.strip(),
        content.strip()
    )


def create_chunks(pages):
    chunks = []

    current_section = None
    current_subsection = None
    current_group = None
    current_policy = None

    current_text = []

    current_pdf_page = None
    current_printed_page = None

    def flush_chunk():
        nonlocal current_text

        if not current_text:
            return

        text = " ".join(
            current_text
        ).strip()

        if text:
            chunks.append({
                "pdf_page": current_pdf_page,
                "printed_page": current_printed_page,
                "section": current_section,
                "subsection": current_subsection,
                "group": current_group,
                "policy": current_policy,
                "text": text
            })

        current_text = []

    def set_current_page(page):
        nonlocal current_pdf_page
        nonlocal current_printed_page

        current_pdf_page = (
            page["pdf_page"]
        )

        current_printed_page = (
            page["printed_page"]
        )

    for page in pages:

        flush_chunk()
        set_current_page(page)

        for raw_line in page["text"].splitlines():
            line = raw_line.strip()

            if not line:
                continue

            # -------------------------
            # SECTION
            # III. EMPLOYEE BENEFITS
            # -------------------------
            if SECTION_PATTERN.match(line):
                flush_chunk()

                current_section = line
                current_subsection = None
                current_group = None
                current_policy = None

            # -------------------------
            # SUBSECTION
            # A. EMPLOYEE LEAVE
            # -------------------------
            elif SUBSECTION_PATTERN.match(line):
                flush_chunk()

                current_subsection = line
                current_group = None
                current_policy = None

            # -------------------------
            # GROUP
            # 2. Leave for International Employees
            # -------------------------
            elif GROUP_PATTERN.match(line):
                flush_chunk()

                current_group = line
                current_policy = None

            # -------------------------
            # POLICY
            # b. Sick Leave: ...
            # -------------------------
            elif POLICY_PATTERN.match(line):
                flush_chunk()

                current_policy, content = (
                    parse_policy_line(line)
                )

                if content:
                    current_text.append(
                        content
                    )

            # -------------------------
            # NORMAL TEXT
            # -------------------------
            else:
                current_text.append(line)

    flush_chunk()

    return chunks


def save_chunks(chunks, output_path):
    with open(
        output_path,
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(
            chunks,
            file,
            indent=4,
            ensure_ascii=False
        )


def main():
    pages = extract_pages(
        PDF_PATH
    )

    chunks = create_chunks(
        pages
    )

    print(
        "Total pages:",
        len(pages)
    )

    print(
        "Total chunks:",
        len(chunks)
    )

    save_chunks(
        chunks,
        OUTPUT_PATH
    )


if __name__ == "__main__":
    main()