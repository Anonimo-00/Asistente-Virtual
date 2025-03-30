import os
import json
from pathlib import Path
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)

class ProjectScanner:
    """Escáner de estructura del proyecto"""
    
    def __init__(self, root_dir: str = "."):
        self.root = Path(root_dir).absolute()
        self.ignored_dirs = {'.git', '__pycache__', 'venv', 'env', 'node_modules'}
        self.ignored_files = {'.gitignore', '*.pyc', '*.pyo', '*.pyd', '.DS_Store'}
    
    def scan(self) -> Dict:
        """Escanea el proyecto y retorna su estructura"""
        try:
            structure = {
                'root': str(self.root),
                'directories': self._scan_directories(),
                'files': self._scan_files(),
                'stats': self._get_stats()
            }
            return structure
        except Exception as e:
            logger.error(f"Error escaneando proyecto: {e}")
            return {}

    def _scan_directories(self) -> List[Dict]:
        """Escanea los directorios del proyecto"""
        directories = []
        
        for dir_path in self.root.rglob('*'):
            if not dir_path.is_dir():
                continue
                
            if any(ignored in dir_path.parts for ignored in self.ignored_dirs):
                continue
            
            rel_path = dir_path.relative_to(self.root)
            directories.append({
                'path': str(rel_path),
                'files': len(list(dir_path.glob('*.*'))),
                'subdirs': len([d for d in dir_path.iterdir() if d.is_dir()])
            })
            
        return sorted(directories, key=lambda x: x['path'])

    def _scan_files(self) -> List[Dict]:
        """Escanea los archivos del proyecto"""
        files = []
        
        for file_path in self.root.rglob('*.*'):
            if not file_path.is_file():
                continue
                
            if any(ignored in file_path.parts for ignored in self.ignored_dirs):
                continue
                
            if any(file_path.match(pattern) for pattern in self.ignored_files):
                continue
            
            rel_path = file_path.relative_to(self.root)
            files.append({
                'path': str(rel_path),
                'size': file_path.stat().st_size,
                'extension': file_path.suffix,
                'modified': file_path.stat().st_mtime
            })
            
        return sorted(files, key=lambda x: x['path'])

    def _get_stats(self) -> Dict:
        """Obtiene estadísticas del proyecto"""
        python_files = list(self.root.rglob('*.py'))
        json_files = list(self.root.rglob('*.json'))
        
        return {
            'total_files': len(list(self.root.rglob('*.*'))),
            'python_files': len(python_files),
            'json_files': len(json_files),
            'total_size': sum(f.stat().st_size for f in self.root.rglob('*.*')),
            'total_dirs': len([d for d in self.root.rglob('*') if d.is_dir()])
        }

    def generate_report(self, output_file: Optional[str] = None) -> None:
        """Genera un reporte de la estructura del proyecto"""
        structure = self.scan()
        
        if not structure:
            logger.error("No se pudo escanear el proyecto")
            return
            
        report = {
            'timestamp': os.path.getmtime(__file__),
            'project': {
                'name': self.root.name,
                'location': str(self.root)
            },
            'structure': structure
        }
        
        if output_file:
            output_path = Path(output_file)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(report, f, indent=2, ensure_ascii=False)
            logger.info(f"Reporte guardado en: {output_file}")
        
        return report

def main():
    """Función principal de ejemplo"""
    scanner = ProjectScanner()
    report = scanner.generate_report("reports/project_structure.json")
    
    # Imprimir resumen
    stats = report['structure']['stats']
    print("\n=== Resumen del Proyecto ===")
    print(f"Archivos totales: {stats['total_files']}")
    print(f"Archivos Python: {stats['python_files']}")
    print(f"Archivos JSON: {stats['json_files']}")
    print(f"Directorios: {stats['total_dirs']}")
    print(f"Tamaño total: {stats['total_size'] / 1024:.2f} KB")
    print("=" * 30)

if __name__ == "__main__":
    main()
