from bs4 import BeautifulSoup

def extract_text_from_html(html_content: str) -> str:
    """Convert HTML email body to plain text."""
    soup = BeautifulSoup(html_content, "html.parser")
    return soup.get_text(separator="\n", strip=True)