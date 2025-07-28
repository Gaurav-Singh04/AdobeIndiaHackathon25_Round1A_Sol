import os
import json
from pathlib import Path
import fitz
from operator import itemgetter
import subprocess

def fonts(doc, granularity=False):
    styles = {}
    font_counts = {}
    for page in doc:
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if granularity:
                            identifier = "{0}_{1}_{2}_{3}".format(s['size'], s['flags'], s['font'], s['color'])
                            styles[identifier] = {'size': s['size'], 'flags': s['flags'], 'font': s['font'], 'color': s['color']}
                        else:
                            identifier = "{0}".format(s['size'])
                            styles[identifier] = {'size': s['size'], 'font': s['font']}
                        font_counts[identifier] = font_counts.get(identifier, 0) + 1
    font_counts = sorted(font_counts.items(), key=itemgetter(1), reverse=True)
    if len(font_counts) < 1:
        raise ValueError("Zero discriminating fonts found!")
    return font_counts, styles

def font_tags(font_counts, styles):
    font_sizes = []
    for (font_size, count) in font_counts:
        font_sizes.append(float(font_size))
    font_sizes = sorted(list(set(font_sizes)), reverse=True)
    heading_sizes = font_sizes[:4]
    size_tag = {}
    for idx, size in enumerate(heading_sizes):
        size_tag[size] = f'<h{idx+1}>'
    for size in font_sizes[4:]:
        size_tag[size] = '<p>'
    return size_tag

def extract_headings(doc, size_tag):
    headings = []
    for page_num, page in enumerate(doc):
        blocks = page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        text = s['text'].strip()
                        if not text:
                            continue
                        tag = size_tag.get(s['size'], '')
                        if tag.startswith('<h'):
                            level = tag[2]
                            if level in '1234':
                                headings.append({
                                    "level": f"H{level}",
                                    "text": text,
                                    "page": page_num + 1
                                })
    return headings

def process_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    font_counts, styles = fonts(doc, granularity=False)
    size_tag = font_tags(font_counts, styles)
    headings = extract_headings(doc, size_tag)
    title = ""
    try:
        first_page = doc[0]
        blocks = first_page.get_text("dict")["blocks"]
        for b in blocks:
            if b['type'] == 0:
                for l in b["lines"]:
                    for s in l["spans"]:
                        t = s['text'].strip()
                        if t:
                            title = t
                            break
                    if title:
                        break
            if title:
                break
    except Exception:
        pass
    # Overwrite title using pdftitle subprocess
    try:
        result = subprocess.run(["pdftitle", "-p", str(pdf_path)], capture_output=True, text=True)
        pdftitle_out = result.stdout.strip().splitlines()
        for line in reversed(pdftitle_out):
            if line.strip():
                title = line.strip()
                break
    except Exception:
        pass
    return {
        "title": title,
        "outline": headings
    }

def process_pdfs():
    input_dir = Path("/app/input")
    output_dir = Path("/app/output")
    output_dir.mkdir(parents=True, exist_ok=True)
    pdf_files = list(input_dir.glob("*.pdf"))
    for pdf_file in pdf_files:
        outline = process_pdf(pdf_file)
        output_file = output_dir / f"{pdf_file.stem}.json"
        with open(output_file, "w", encoding="utf-8") as f:
            json.dump(outline, f, indent=2, ensure_ascii=False)
        print(f"Processed {pdf_file.name} -> {output_file.name}")

if __name__ == "__main__":
    print("Starting processing pdfs")
    process_pdfs()
    print("completed processing pdfs")
