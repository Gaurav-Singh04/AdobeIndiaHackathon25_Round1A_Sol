# PDF Outline Extractor

## Overview
This solution extracts a structured outline from PDF documents. For each PDF, it finds the document title and headings (H1, H2, H3, H4) and outputs them in a clean JSON format. The output includes the heading level, text, and page number for each heading.

## How It Works
- The script scans all PDF files in `/app/input`.
- For each PDF, it analyzes font sizes to identify headings and their levels.
- The document title is extracted using the `pdftitle` command-line tool for best accuracy.
- The results are saved as JSON files in `/app/output`, with one JSON file per PDF.

## Dependencies
- Python 3.10 or newer
- PyMuPDF (`pymupdf`)
- pdftitle (for title extraction)

All dependencies are installed in the Docker container.

## Approach
- For each PDF, the script uses PyMuPDF to analyze the font sizes of all text spans on every page.
- It collects all unique font sizes and sorts them from largest to smallest. The largest four sizes are mapped to heading levels H1, H2, H3, and H4.
- Any text span using one of these four sizes is considered a heading, and its level, text, and page number are recorded in the output.
- The document title is extracted using the `pdftitle` command-line tool, which uses both PDF metadata and content heuristics to find the most likely title. This is more reliable than simply taking the first line or the largest text.
- The final output is a JSON file containing the extracted title and a list of all detected headings, each with its level and page number.
- The solution does not rely on any hardcoded rules or file-specific logic, and works entirely offline.

