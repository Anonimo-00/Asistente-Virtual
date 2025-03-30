import os
from pathlib import Path
from typing import List, Dict
import json

def scan_project_structure(root_dir: str) -> Dict:
    """Escanea y analiza la estructura completa del proyecto, incluyendo todos los archivos."""
    ignored_dirs = {'.git', '__pycache__', '.pytest_cache', 'venv'}  # Folders to ignore, but not files
    
    root = Path(root_dir)
    structure = {
        'root': str(root.absolute()),
        'directories': {},
        'stats': {
            'total_files': 0,
            'by_extension': {},
            'total_size': 0,
            'total_dirs': 0
        }
    }
    
    def scan_directory(directory: Path) -> Dict:
        result = {
            'name': directory.name,
            'path': str(directory.relative_to(root)),
            'files': [],
            'subdirs': [],
            'stats': {
                'files_count': 0,
                'total_size': 0,
                'extensions': {}
            }
        }
        
        try:
            items = [x for x in directory.iterdir()] # No filter here, get all items
            
            # Process files
            for item in items:
                if item.is_file():
                    file_info = {
                        'name': item.name,
                        'size': item.stat().st_size,
                        'extension': item.suffix,
                        'modified': item.stat().st_mtime
                    }
                    result['files'].append(file_info)
                    result['stats']['files_count'] += 1
                    result['stats']['total_size'] += file_info['size']
                    result['stats']['extensions'][item.suffix] = \
                        result['stats']['extensions'].get(item.suffix, 0) + 1
                    
                    # Update global stats
                    structure['stats']['total_files'] += 1
                    structure['stats']['total_size'] += file_info['size']
                    structure['stats']['by_extension'][item.suffix] = \
                        structure['stats']['by_extension'].get(item.suffix, 0) + 1
                
                # Process subdirectories
                elif item.is_dir():
                    if item.name not in ignored_dirs: # Filter only directories
                        subdir_info = scan_directory(item)
                        result['subdirs'].append(subdir_info)
                        structure['stats']['total_dirs'] += 1
            
            return result
            
        except PermissionError:
            return result

    def print_tree(directory_info: Dict, prefix: str = "", is_last: bool = True, output_file=None):
        """Imprime la estructura en forma de árbol"""
        # Marcar directorio
        marker = "└──" if is_last else "├──"
        line = f"{prefix}{marker} {directory_info['name']}/"
        print(line)
        if output_file:
            output_file.write(line + "\n")
        
        new_prefix = prefix + ("    " if is_last else "│   ")
        
        # Imprimir subdirectorios
        for i, subdir in enumerate(directory_info['subdirs']):
            is_last_subdir = i == len(directory_info['subdirs']) - 1 and not directory_info['files']
            print_tree(subdir, new_prefix, is_last_subdir, output_file)
        
        # Imprimir archivos
        for i, file in enumerate(directory_info['files']):
            marker = "└──" if i == len(directory_info['files']) - 1 else "├──"
            size_kb = file['size'] / 1024
            line = f"{new_prefix}{marker} {file['name']} ({size_kb:.1f} KB)"
            print(line)
            if output_file:
                output_file.write(line + "\n")

    # Start scanning
    print("\n=== Escaneando Proyecto ===")
    structure['directories'] = scan_directory(root)
    
    # Save report to txt
    report_txt_file = root / "reports" / "project_structure.txt"
    report_txt_file.parent.mkdir(exist_ok=True)
    with open(report_txt_file, "w", encoding="utf-8") as txt_file:
        txt_file.write("=== Estructura del Proyecto ===\n")
        txt_file.write(f"Raíz: {structure['root']}\n\n")
        print("\n=== Estructura del Proyecto ===")
        print(f"Raíz: {structure['root']}\n")
        print_tree(structure['directories'], output_file=txt_file)

        txt_file.write("\n=== Estadísticas ===\n")
        txt_file.write(f"Archivos totales: {structure['stats']['total_files']}\n")
        txt_file.write(f"Directorios: {structure['stats']['total_dirs']}\n")
        txt_file.write(f"Tamaño total: {structure['stats']['total_size']/1024/1024:.2f} MB\n")
        txt_file.write("\nExtensiones encontradas:\n")
        print("\n=== Estadísticas ===")
        print(f"Archivos totales: {structure['stats']['total_files']}")
        print(f"Directorios: {structure['stats']['total_dirs']}")
        print(f"Tamaño total: {structure['stats']['total_size']/1024/1024:.2f} MB")
        print("\nExtensiones encontradas:")
        for ext, count in structure['stats']['by_extension'].items():
            txt_file.write(f"  {ext or 'sin extensión'}: {count} archivos\n")
            print(f"  {ext or 'sin extensión'}: {count} archivos")
    print(f"\nReporte detallado guardado en: {report_txt_file}")

    # Save report to json
    report_json_file = root / "reports" / "project_structure.json"
    report_json_file.parent.mkdir(exist_ok=True)
    with open(report_json_file, "w", encoding="utf-8") as f:
        json.dump(structure, f, indent=2, ensure_ascii=False)
    print(f"\nReporte detallado guardado en: {report_json_file}")
    
    return structure

def main():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    scan_project_structure(current_dir)

if __name__ == "__main__":
    main()
