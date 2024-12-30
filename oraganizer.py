import os
import re

def parse_m3u(file_path):
    groups = {}
    current_group = None
    current_entry = []

    with open(file_path, 'r', encoding='utf-8') as file:
        for line in file:
            line = line.strip()
            if line.startswith("#EXTINF:"):
                # Extraindo o group-title usando regex
                match = re.search(r'group-title="(.*?)"', line)
                if match:
                    current_group = match.group(1)
                    if current_group not in groups:
                        groups[current_group] = []
                current_entry = [line]
            elif line.startswith("http"):
                current_entry.append(line)
                if current_group:
                    groups[current_group].append("\n".join(current_entry))
                current_entry = []

    return groups

def save_groups(groups, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    for group, entries in groups.items():
        # Substituir caracteres inválidos em nomes de arquivo
        sanitized_group = re.sub(r'[<>:"/\\|?*]', '_', group)
        file_path = os.path.join(output_dir, f"{sanitized_group}.m3u")
        with open(file_path, 'w', encoding='utf-8') as file:
            file.write("#EXTM3U\n")
            file.write("\n".join(entries))
        print(f"Grupo '{group}' salvo em: {file_path}")

def main():
    input_file = "lista.m3u"  # Substitua pelo caminho da sua lista M3U
    output_dir = "m3u_files"

    print("Lendo e processando a lista M3U...")
    groups = parse_m3u(input_file)
    print("Exportando grupos para arquivos separados...")
    save_groups(groups, output_dir)
    print("Processo concluído!")

if __name__ == "__main__":
    main()
