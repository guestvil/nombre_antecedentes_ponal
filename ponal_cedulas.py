import pandas as pd
import pymupdf
from playwright.sync_api import sync_playwright
from playwright._impl._errors import TimeoutError
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
        user_data = {'id': str(row[1]),
                     'id_type': row[2],
                     'name_list': str(row[3]).upper().split() + str(row[4]).upper().split()}
        total_data.append(user_data)
    return total_data


def get_name_ponal(users_info: dict):
    with sync_playwright() as playwright:
        browser = playwright.chromium.launch_persistent_context(user_data_dir='', headless=False, ignore_default_args=['--enable-automation'], args=[
        f"--disable-extensions-except=./chromium_automation",
        f"--load-extension=./chromium_automation",])
        ponal_page = browser.new_page()
        real_names = []
        ponal_page.goto('https://antecedentes.policia.gov.co:7005/WebJudicial/')
        for user_info in users_info:
            if user_info['id_type'] == 'PEP':
                continue
            ponal_page.locator("#aceptaOption\\:0").click()
            ponal_page.get_by_role('button', name='Enviar').click()
            try: 
                # ponal_page.wait_for_timeout(10000)
                # ponal_page.locator('div#captchaAntecedentes').click()
                # Locate the iframe first
                captcha_iframe = ponal_page.frame_locator('iframe[title="reCAPTCHA"]')
                # Wait until the checkmark appears inside the iframe
                captcha_iframe.locator('.recaptcha-checkbox-checkmark').wait_for(state='visible', timeout=40000)  # Max 35 sec
            except TimeoutError as e:
                print(e)
                ponal_page.goto('https://antecedentes.policia.gov.co:7005/WebJudicial/')
                continue
            # ponal_page.wait_for_timeout(5000)
            if user_info['id_type'] != 'CC':
                continue
            ponal_page.get_by_role('textbox').fill(user_info['id'])
            ponal_page.get_by_role('button', name='Consultar').click()
            ponal_html = ponal_page.locator('span#form\\:mensajeCiudadano').inner_html()
            html_bs = BeautifulSoup(ponal_html, 'html.parser')
            list_of_text = list(html_bs.stripped_strings)
            for index, text in enumerate(list_of_text):
                if text.strip() == 'Apellidos y Nombres:':
                    name = list_of_text[index + 1]
                    name = name.upper().split()
                    user_real_info = {'id': user_info['id_type'], 'name': name}
                    break
                else: 
                    user_info = None
                    continue
            if user_info != None: 
                real_names.append(user_real_info)
            ponal_page.get_by_role('button', name='Volver al inicio').click()
    return real_names


def main():
    users_data = get_documents(excel_path='usuarios_wplay.xlsx')
    print('The data list has ', len(users_data), ' elements')
    for user_info in users_data[4:40]:
        print(user_info)
    real_names = get_name_ponal(users_data[4:40])

    


if __name__ == '__main__':
    main()