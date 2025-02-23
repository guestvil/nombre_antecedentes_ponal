import pymupdf
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup

def get_cedulas(pdf_test: str):
    '''Retuns a list of list containing: [cedula, name]'''
    table_elements = []
    with pymupdf.open(pdf_test) as file:
        for page in file:
            tab = page.find_tables()
            tab_text = tab[0].extract()
            for a_list in tab_text[1:]:
                table_elements.append(a_list[:2])
    # for elemento in table_elements:
      #  print(elemento)
    return table_elements

def main():
    cedulas_list = get_cedulas(pdf_test='Jurados de votación.pdf')
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(user_data_dir='', headless=False, ignore_default_args=['--enable-automation'], args=[
        f"--disable-extensions-except=./chromium_automation",
        f"--load-extension=./chromium_automation",])
        ponal_page = browser.new_page()
        ponal_page.goto('https://antecedentes.policia.gov.co:7005/WebJudicial/')
        ponal_page.locator("#aceptaOption\\:0").click()
        ponal_page.get_by_role('button', name='Enviar').click()
        ponal_page.locator('div#captchaAntecedentes').click()
        ponal_page.wait_for_timeout(5000)
        ponal_page.get_by_role('textbox').fill('79940745')
        ponal_page.get_by_role('button', name='Consultar').click()
        ponal_html = ponal_page.locator('span#form\\:mensajeCiudadano').inner_html()
        html_bs = BeautifulSoup(ponal_html, 'html.parser')
        list_of_text = list(html_bs.stripped_strings)
        for index, text in enumerate(list_of_text):
            if text.strip() == 'Apellidos y Nombres:':
                name = list_of_text[index + 1]
        print(name)
    return None


if __name__ == '__main__':
    main()