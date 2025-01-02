import os
import re
import requests
from urllib.parse import urlparse
from tqdm import tqdm
import unicodedata

def parse_m3u(file_path):
    content = []
    current_item = {}
    
    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#EXTINF'):
                match = re.search(r'tvg-name="([^"]+)"', line)
                current_item['title'] = match.group(1) if match else "Unknown"
                
                match = re.search(r'tvg-logo="([^"]+)"', line)
                current_item['logo'] = match.group(1) if match else None
                
                match = re.search(r'group-title="([^"]+)"', line)
                current_item['group'] = match.group(1) if match else "Ungrouped"
            elif line.startswith('http'):
                if line.endswith('.mp4'):
                    current_item['url'] = line
                    content.append(current_item)
                current_item = {}
    
    return content

def sanitize_filename(name):
    """Remove caracteres inválidos e normaliza o nome."""
    name = unicodedata.normalize('NFKD', name)  # Remove acentos
    name = name.encode('ascii', 'ignore').decode('ascii')  # Remove caracteres não ASCII
    name = re.sub(r'[<>:"/\\|?*\x00-\x1F]', '_', name)  # Substitui caracteres problemáticos
    name = re.sub(r'\s+', ' ', name).strip()  # Remove espaços extras
    return name

def extract_filename_from_url(url):
    """Extrai o nome do arquivo de uma URL."""
    parsed_url = urlparse(url)
    return os.path.basename(parsed_url.path)

def download_file(url, dest_path):
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0',
        }

        with requests.get(url, stream=True, headers=headers) as response:
            response.raise_for_status()
            total_size = int(response.headers.get('content-length', 0))
            chunk_size = 8192

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
        
        group_dir = os.path.join(base_dir, group)
        os.makedirs(group_dir, exist_ok=True)
        
        movie_dir = os.path.join(group_dir, title)
        os.makedirs(movie_dir, exist_ok=True)
        
        video_path = os.path.join(movie_dir, f"{title}.mp4")
        
        if item['logo']:
            logo_name = sanitize_filename(extract_filename_from_url(item['logo']))
            logo_path = os.path.join(movie_dir, logo_name)
        else:
            logo_path = None
        
        if not os.path.exists(video_path):
            print(f"Baixando vídeo: {item['title']}...")
            download_file(item['url'], video_path)
        else:
            print(f"Arquivo de vídeo já existe, ignorando: {video_path}")
        
        if item['logo']:
            if not os.path.exists(logo_path):
                print(f"Baixando logotipo: {item['title']}...")
                download_file(item['logo'], logo_path)
            else:
                print(f"Logotipo já existe, ignorando: {logo_path}")
        else:
            print(f"Nenhum logotipo encontrado para: {item['title']}")

def process_all_m3u_files(directory, base_dir='downloads'):
    for filename in os.listdir(directory):
        if filename.endswith('.m3u'):
            file_path = os.path.join(directory, filename)
            print(f"Processando arquivo: {file_path}")
            content = parse_m3u(file_path)
            create_folders_and_download(content, base_dir=base_dir)

m3u_directory = 'm3u_files'
process_all_m3u_files(m3u_directory)
