import base64
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options as ChromeOptions


def generate_pdf_from_url(url):
    """
    Generate A4 landscape PDF from a URL.

    Args:
        url: The URL to render as PDF

    Returns:
        bytes: PDF file content
    """
    # A4 Landscape print options (297mm x 210mm)
    print_options = {
        "landscape": True,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,  # Use CSS @page size
        "paperWidth": 11.69,  # 297mm in inches
        "paperHeight": 8.27,  # 210mm in inches
        "marginTop": 0,
        "marginBottom": 0,
        "marginRight": 0,
        "marginLeft": 0,
    }

    # Configure Chrome options
    webdriver_options = ChromeOptions()
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-extensions")
    webdriver_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        start_time = time.time()
        print(f"Starting PDF generation for: {url}")

        driver = webdriver.Chrome(options=webdriver_options)
        driver.get(url)

        # Wait for page to load
        time.sleep(3)

        # Generate PDF using Chrome DevTools Protocol
        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        pdf_bytes = base64.b64decode(result["data"])

        print(f"PDF generated in {time.time() - start_time:.2f} seconds")
        return pdf_bytes

    except Exception as err:
        print(f"Error generating PDF: {err}")
        raise
    finally:
        if driver:
            driver.quit()


def generate_pdf_from_html(html_content, base_url="http://localhost:8000"):
    """
    Generate A4 landscape PDF from HTML content.

    Args:
        html_content: HTML string to render as PDF
        base_url: Base URL for resolving relative paths

    Returns:
        bytes: PDF file content
    """
    # A4 Landscape print options
    print_options = {
        "landscape": True,
        "displayHeaderFooter": False,
        "printBackground": True,
        "preferCSSPageSize": True,
        "paperWidth": 11.69,
        "paperHeight": 8.27,
        "marginTop": 0,
        "marginBottom": 0,
        "marginRight": 0,
        "marginLeft": 0,
    }

    webdriver_options = ChromeOptions()
    webdriver_options.add_argument("--headless")
    webdriver_options.add_argument("--disable-gpu")
    webdriver_options.add_argument("--no-sandbox")
    webdriver_options.add_argument("--disable-extensions")
    webdriver_options.add_argument("--disable-dev-shm-usage")

    driver = None
    try:
        start_time = time.time()
        print("Starting PDF generation from HTML content")

        driver = webdriver.Chrome(options=webdriver_options)
        driver.get(base_url)

        # Inject HTML content
        driver.execute_script(
            "document.open(); document.write(arguments[0]); document.close();",
            html_content,
        )

        # Wait for document to be ready
        driver.execute_script("""
            return new Promise((resolve) => {
                if (document.readyState === 'complete') {
                    resolve();
                } else {
                    window.addEventListener('load', resolve);
                }
            });
        """)

        time.sleep(3)

        result = driver.execute_cdp_cmd("Page.printToPDF", print_options)
        pdf_bytes = base64.b64decode(result["data"])

        print(f"PDF generated in {time.time() - start_time:.2f} seconds")
        return pdf_bytes

    except Exception as err:
        print(f"Error generating PDF: {err}")
        raise
    finally:
        if driver:
            driver.quit()
