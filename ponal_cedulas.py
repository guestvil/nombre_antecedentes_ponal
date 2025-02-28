import pandas as pd
import pymupdf
from playwright.sync_api import sync_playwright
from bs4 import BeautifulSoup
import unicodedata

def remove_accents(text):
    return ''.join(c for c in unicodedata.normalize('NFD', text) if unicodedata.category(c) != 'Mn')



def get_documents(excel_path: str):
    total_data = []
    old_excel_file = pd.read_excel(excel_path, header=None, engine='openpyxl')
    old_excel_file = old_excel_file.applymap(lambda x: remove_accents(str(x)) if isinstance(x, str) else x)
    old_excel_file.to_excel('cleaned_file.xlsx', index=False)
    excel_file = pd.read_excel('cleaned_file.xlsx', header=None, engine='openpyxl')
    for row in excel_file.itertuples(index=True):
        user_data = {'id': row[1],
                     'id_type': row[2],
                     'name_list': str(row[3]).upper().split() + str(row[4]).upper().split()}
        total_data.append(user_data)
    return total_data


def get_name_ponal(user_info: dict):
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

def main():
    users_data = get_documents(excel_path='usuarios_wplay.xlsx')
    print('The data list has ', len(users_data), ' elements')
    for user_infor in users_data[1:40]:
        print(user_infor)


if __name__ == '__main__':
    main()