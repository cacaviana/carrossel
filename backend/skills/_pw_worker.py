"""Worker Playwright - roda em subprocess separado pra evitar conflito de event loop."""
import base64
import json
import sys

from playwright.sync_api import sync_playwright


def main():
    job_path = sys.argv[1]
    with open(job_path, "r", encoding="utf-8") as f:
        job = json.load(f)

    htmls = job["htmls"]
    width = job["width"]
    height = job["height"]

    resultado = []
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": width, "height": height})

        for item in htmls:
            page.set_content(item["html"], wait_until="networkidle")
            screenshot = page.screenshot(type="jpeg", quality=90)
            b64 = base64.b64encode(screenshot).decode()
            resultado.append({
                "slide_index": item["idx"],
                "titulo": item["titulo"],
                "image_base64": f"data:image/jpeg;base64,{b64}",
            })

        browser.close()

    # Escrever resultado em arquivo (evita encoding issues no stdout)
    output_path = job_path.replace(".json", "_output.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(resultado, f, ensure_ascii=False)
    print(output_path)


if __name__ == "__main__":
    main()
