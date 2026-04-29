"""Batch convert HTML presentations to PPTX and PDF.

Entry point for the PPTX processing pipeline.
"""

import glob
import os

from pptx_processor.config import INPUT_DIR, SCREENSHOTS_DIR, OUTPUT_DIR
from pptx_processor.capture import capture_slides
from pptx_processor.export import export_to_pptx, export_to_pdf


def main():
    print("Batch presentation conversion started\n")

    os.makedirs(SCREENSHOTS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    html_files = glob.glob(os.path.join(INPUT_DIR, "*.html"))

    for html_file in html_files:
        images, base_name = capture_slides(html_file)
        if not images:
            print(f"[SKIP] No slides captured for {html_file}\n")
            continue
        pptx_path = export_to_pptx(images, base_name)
        pdf_path = export_to_pdf(images, base_name)
        print(f"[DONE] {pptx_path} + {pdf_path}\n")

    print("All tasks completed successfully!")


if __name__ == "__main__":
    main()
