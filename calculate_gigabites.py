import os
import re
import aiohttp
import asyncio

def parse_m3u(file_path):
    content = []
    current_item = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#EXTINF'):
                # Extrai informações do #EXTINF
                match = re.search(r'tvg-name="([^"]+)"', line)
                current_item['title'] = match.group(1) if match else "Unknown"
                
                match = re.search(r'tvg-logo="([^"]+)"', line)
                current_item['logo'] = match.group(1) if match else None
                
                match = re.search(r'group-title="([^"]+)"', line)
                current_item['group'] = match.group(1) if match else "Ungrouped"
            elif line.startswith('http'):
                # Verifica se o link tem a extensão .mp4
                if line.endswith('.mp4'):
                    # Associa o link ao item atual e adiciona à lista
                    current_item['url'] = line
                    content.append(current_item)
                current_item = {}
    
    return content

async def get_file_size(url, session):
    """Tenta obter o tamanho do arquivo usando o método GET com Range."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Range': 'bytes=0-1'
        }
        async with session.get(url, headers=headers, allow_redirects=True) as response:
            if response.status in [200, 206]:  # Sucesso ou conteúdo parcial
                content_length = response.headers.get('Content-Range') or response.headers.get('Content-Length')
                if content_length:
                    size = int(content_length.split('/')[-1])
                    print(f"Arquivo: {url} | Tamanho: {size / (1024 ** 2):.2f} MB")
                    return size
                else:
                    print(f"Não foi possível determinar o tamanho para: {url}")
                    return 0
            else:
                print(f"URL ignorada devido ao status {response.status}: {url}")
                return 0
    except Exception as e:
        print(f"Erro ao obter tamanho do arquivo para {url}: {e}")
        return 0

async def calculate_total_size(content):
    """Calcula o tamanho total de todos os arquivos em bytes de forma assíncrona."""
    total_size = 0
    async with aiohttp.ClientSession() as session:
        tasks = [get_file_size(item['url'], session) for item in content if 'url' in item]
        sizes = await asyncio.gather(*tasks)
        total_size = sum(sizes)
    return total_size

async def process_all_m3u_files(directory):
    """Processa todos os arquivos .m3u em um diretório e calcula o tamanho total."""
    total_size = 0
    for filename in os.listdir(directory):
        if filename.endswith('.m3u'):
            file_path = os.path.join(directory, filename)
            print(f"Processando arquivo: {file_path}")
            content = parse_m3u(file_path)
            file_total_size = await calculate_total_size(content)
            total_size += file_total_size
            print(f"Tamanho total para {filename}: {file_total_size / (1024 ** 3):.2f} GB\n")
    return total_size

def main():
    # Diretório onde estão os arquivos .m3u
    m3u_directory = 'm3u_files'
    total_size_bytes = asyncio.run(process_all_m3u_files(m3u_directory))
    
    # Converte bytes para gigabytes
    total_size_gb = total_size_bytes / (1024 ** 3)
    print(f"Tamanho total necessário para armazenar os arquivos: {total_size_gb:.2f} GB")

# Chama o script
if __name__ == '__main__':
    main()
