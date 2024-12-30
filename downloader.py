import os
import re
import requests
from urllib.parse import urlparse
from tqdm import tqdm

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

def sanitize_filename(name):
    """Remove caracteres inválidos do nome do arquivo ou pasta."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)

def extract_filename_from_url(url):
    """Extrai o nome do arquivo de uma URL."""
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)

def download_file(url, dest_path):
    """Faz o download de um arquivo de uma URL para o caminho especificado com barra de progresso."""
    try:
        # Definindo cabeçalhos para emular um navegador
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Connection': 'keep-alive'
        }

        # Realiza a requisição HTTP com os cabeçalhos
        with requests.get(url, stream=True, headers=headers) as response:
            response.raise_for_status()  # Vai lançar um erro se o status for 4xx ou 5xx
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192  # Tamanho dos pedaços para download

            # Realiza o download com barra de progresso
            with open(dest_path, 'wb') as f, tqdm(
                total=total_size,
                unit='B',
                unit_scale=True,
                desc=os.path.basename(dest_path),
                ncols=80
            ) as progress:
                for chunk in response.iter_content(chunk_size=chunk_size):
                    f.write(chunk)
                    progress.update(len(chunk))

        print(f"Download concluído: {dest_path}")
    except Exception as e:
        print(f"Erro ao baixar {url}: {e}")

def create_folders_and_download(content, base_dir='downloads'):
    os.makedirs(base_dir, exist_ok=True)
    
    for item in content:
        group = sanitize_filename(item['group']) if item['group'] else "Ungrouped"
        title = sanitize_filename(item['title']) if item['title'] else "Unknown"
        
        # Cria a estrutura de pastas
        group_dir = os.path.join(base_dir, group)
        os.makedirs(group_dir, exist_ok=True)
        
        movie_dir = os.path.join(group_dir, title)
        os.makedirs(movie_dir, exist_ok=True)
        
        # Caminho do arquivo de vídeo (nomeado com o título)
        video_path = os.path.join(movie_dir, f"{title}.mp4")
        
        # Caminho do arquivo de logotipo (nome original)
        if item['logo']:
            logo_name = extract_filename_from_url(item['logo'])
            logo_path = os.path.join(movie_dir, logo_name)
        else:
            logo_path = None
        
        # Download do vídeo
        if not os.path.exists(video_path):
            print(f"Baixando vídeo: {item['title']}...")
            download_file(item['url'], video_path)
        else:
            print(f"Arquivo de vídeo já existe, ignorando: {video_path}")
        
        # Download do logotipo (se disponível)
        if item['logo']:
            if not os.path.exists(logo_path):
                print(f"Baixando logotipo: {item['title']}...")
                download_file(item['logo'], logo_path)
            else:
                print(f"Logotipo já existe, ignorando: {logo_path}")
        else:
            print(f"Nenhum logotipo encontrado para: {item['title']}")

def process_all_m3u_files(directory, base_dir='downloads'):
    """Processa todos os arquivos .m3u em um diretório."""
    for filename in os.listdir(directory):
        if filename.endswith('.m3u'):
            file_path = os.path.join(directory, filename)
            print(f"Processando arquivo: {file_path}")
            content = parse_m3u(file_path)
            create_folders_and_download(content, base_dir=base_dir)

# Uso do script
m3u_directory = 'm3u_files'  # Substitua pelo diretório onde estão os arquivos .m3u
process_all_m3u_files(m3u_directory)
