import os
import time
import random
import logging
from datetime import datetime
from pathlib import Path
from flask import jsonify
from PIL import Image, ImageDraw, ImageFont
import io
import base64

# Configuração de logging
logger = logging.getLogger(__name__)

class ImageController:
    """Controlador para operações com imagens PNG."""
    
    def __init__(self, image_directory="static/images"):
        """
        Inicializa o controlador de imagens.
        
        Args:
            image_directory (str): Diretório onde as imagens serão salvas
        """
        self.image_directory = image_directory
        
        # Garantir que o diretório existe
        os.makedirs(image_directory, exist_ok=True)
    
    def remove_old_files(self, minutes=10):
        """
        Remove arquivos antigos do diretório de imagens.
        
        Args:
            minutes (int): Arquivos mais antigos que este valor serão removidos
        """
        current_time = time.time()
        directory = self.image_directory
        
        if not os.path.exists(directory):
            logger.warning(f"Diretório {directory} não existe")
            return
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            
            if os.path.isfile(file_path):
                creation_time = os.path.getctime(file_path)
                time_difference = (current_time - creation_time) / 60
                
                if time_difference > minutes:
                    os.remove(file_path)
                    logger.info(f"Arquivo removido: {filename}")
                else:
                    logger.debug(f"{filename} criado há menos de {minutes} minutos.")
    
    def get_most_recent_file(self, rename_pattern="desenho_{random}"):
        """
        Obtém o arquivo mais recente do diretório e o renomeia.
        
        Args:
            rename_pattern (str): Padrão para renomear o arquivo. Use {random} para número aleatório
            
        Returns:
            str: Nome do arquivo renomeado
            
        Raises:
            FileNotFoundError: Se o diretório não existir ou não houver arquivos
        """
        directory = self.image_directory
        
        if not os.path.isdir(directory):
            raise FileNotFoundError(f"O diretório {directory} não foi encontrado.")
        
        files = [f for f in Path(directory).iterdir() if f.is_file()]
        
        if not files:
            raise FileNotFoundError("Não há arquivos no diretório.")
        
        most_recent_file = max(files, key=os.path.getmtime)
        
        random_number = random.randint(10000, 99999)
        
        new_name = rename_pattern.format(random=random_number) + most_recent_file.suffix
        new_path = most_recent_file.parent / new_name
        
        os.rename(most_recent_file, new_path)
        
        return new_path.name
    
    
    def check_image_exists(self, filename):
        """
        Verifica se um arquivo de imagem existe.
        
        Args:
            filename (str): Nome do arquivo
            
        Returns:
            bool: True se o arquivo existir, False caso contrário
        """
        file_path = os.path.join(self.image_directory, filename)
        return os.path.exists(file_path)
    
    def get_image_path(self, filename):
        """
        Obtém o caminho completo de um arquivo de imagem.
        
        Args:
            filename (str): Nome do arquivo
            
        Returns:
            str: Caminho completo do arquivo
        """
        return os.path.join(self.image_directory, filename)
    
    def list_images(self, filter_extension='.png'):
        """
        Lista todos os arquivos de imagem no diretório.
        
        Args:
            filter_extension (str): Extensão para filtrar (ex: '.png')
            
        Returns:
            list: Lista de nomes de arquivos
        """
        if not os.path.exists(self.image_directory):
            return []
        
        return [f for f in os.listdir(self.image_directory) 
                if os.path.isfile(os.path.join(self.image_directory, f)) 
                and f.lower().endswith(filter_extension)]

# Funções de conveniência para compatibilidade com o código existente
def remove_old_files(minutes=10, directory="static/images"):
    """Função de conveniência para remover arquivos antigos."""
    controller = ImageController(image_directory=directory)
    controller.remove_old_files(minutes)

def get_most_recent_file(directory="static/images"):
    """Função de conveniência para obter o arquivo mais recente."""
    controller = ImageController(image_directory=directory)
    return controller.get_most_recent_file()