import requests
from bs4 import BeautifulSoup
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By
import re
import time
import os

headers = {
    'user-agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/113.0.0.0 Safari/537.36"
}

# Links contendo 20 placas de vídeo por página
links_kabum = [str("https://www.kabum.com.br/hardware/placa-de-video-vga?page_number={}&page_size=20&facet_filters=&sort=most_searched").format(i)
               for i in range(1, 2)]

driver = webdriver.Chrome()

# Features
data = {
    "Titulo": [],
    "Marca": [],
    "Modelo": [],
    "Preco": [],
    "Tamanho da Memoria (GB)": [],
    "Tipo da Memoria": [],
    "Interface da Memoria (Bits)": [],
    "Link": []
}

for link in links_kabum:
    req = requests.get(link, headers=headers)
    soup = BeautifulSoup(req.text, 'html.parser')
    products = soup.find_all(class_='productCard')

    for product in products:
        product_path = (product.find('a'))['href']
        product_link = str(f"https://www.kabum.com.br{product_path}")

        product_req = requests.get(product_link, headers=headers)
        product_soup = BeautifulSoup(product_req.text, 'html.parser')

        print("Link do produto: ")
        print(product_link)

        try:
            driver.get(product_link)
            # Espera de 2 segundos para garantir que a página carregue
            time.sleep(2)
            info = driver.find_element(By.CLASS_NAME, "sc-7e0ca514-1")
            info_string = info.text

            # Marca
            brand_match = re.search(r'Marca:\s*(\w+)', info_string)
            if brand_match:
                brand = brand_match.group(1)
                data["Marca"].append(brand)
                print("Marca:", brand)
            else:
                data["Marca"].append("")

            # Modelo
            model_match = re.search(r'Modelo:\s*(\w+)', info_string)
            if model_match:
                model = model_match.group(1)
                data["Modelo"].append(model)
                print("Modelo:", model)
            else:
                data["Modelo"].append("")

            # Interface de Memória
            interface_match = re.search(r'Interface:\s*(.+)', info_string)
            if interface_match:
                interface = interface_match.group(1)
                data["Interface da Memoria (Bits)"].append(interface)
                print("Interface da Memória:", interface)
            else:
                data["Interface da Memoria (Bits)"].append("")

            # Tamanho da Memória
            memory_size_match = re.search(
                r'Configuração de memória padrão:\s*(\d+)\s*GB', info_string)
            if memory_size_match:
                memory_size = memory_size_match.group(1)
                data["Tamanho da Memoria (GB)"].append(memory_size)
                print("Tamanho da Memória:", memory_size)
            else:
                data["Tamanho da Memoria (GB)"].append("")

        except NoSuchElementException:
            print("Informações técnicas não encontradas para:", product_link)
            continue
        except Exception as e:
            print(f"Erro ao acessar informações técnicas: {e}")
            continue

        # Adicionando o link do produto
        data["Link"].append(product_link)

# Certificando-se de que todos os arrays têm o mesmo comprimento
max_len = max(len(data[key]) for key in data)
for key in data:
    data[key] += [""] * (max_len - len(data[key]))

# Criando DataFrame
df = pd.DataFrame(data)

# Removendo acentuações do cabeçalho
df.columns = df.columns.str.normalize('NFKD').str.encode(
    'ascii', errors='ignore').str.decode('utf-8')

# Salvando o Excel no mesmo diretório que o script
current_directory = os.path.dirname(os.path.abspath(__file__))
excel_path = os.path.join(current_directory, 'placas_de_video_kabum.xlsx')
df.to_excel(excel_path, index=False)
