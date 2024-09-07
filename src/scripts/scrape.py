import wikipedia
import pdfkit

def save_page_to_pdf(page_title, output_path):
    # Fetch the Wikipedia page content
    page_content = wikipedia.page(page_title).content

    # Write the content to a temporary HTML file
    
    with open(output_path, "w", encoding="utf-8") as file:
        file.write(page_content)


if __name__ == "__main__":
    # Define the page title and output PDF path
    page_title = "MachineLearning"
    output_path = "machine_learning.txt"

    # Save the page content as a PDF
    save_page_to_pdf(page_title, output_path)

    print(f"Page '{page_title}' saved as file: {output_path}")



