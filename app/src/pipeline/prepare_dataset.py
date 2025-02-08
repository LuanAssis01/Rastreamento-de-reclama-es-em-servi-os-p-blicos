import json
from enum import Enum
import logging
import os
import sys

logger = logging.getLogger(__name__)

class DatasetStatus(Enum):
    LOADED = 1
    CHANGED = 2
    RELEASED = 3

class LabelStudioProcessor:
    DATA_FOLDER = '/home/luan/Documentos/Trabalho_Final_BD/dataset/'
    OUTPUT_FOLDER = os.path.join(DATA_FOLDER, 'output')  # Definindo a pasta de saída

    def __init__(self, dataset_file):
        self.dataset_file = dataset_file
        self.dataset_name, ext = os.path.splitext(self.dataset_file)
        # Usando os.path.join para garantir que o caminho seja correto
        dataset_path = os.path.join(self.DATA_FOLDER, self.dataset_file)
        with open(dataset_path, encoding='utf-8') as file:
            self.dataset = json.load(file)
        self._dataset_status = DatasetStatus.LOADED

    def to_label_studio_format(self):
        logger.info(f'Dataset {self.dataset_file} processando. Status: {self._dataset_status}.')
        self.dataset = [
            {key: entry.get(key, None) for key in ["Data_Reclamacao", "Órgão", "Local", "Setor", "Descrição", "Status", "Data_Resolucao"]}
            for entry in self.dataset
        ]
        self._dataset_status = DatasetStatus.CHANGED
        logger.info(f'Dataset {self.dataset_file} processado. Status alterado para {self._dataset_status}.')
        return self
    
    def export_dataset(self):
        # Criar a pasta output se não existir
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

        logger.info(f'Dataset {self.dataset_file} iniciando exportação. Status: {self._dataset_status}.')
        output_filename = self.dataset_name + '_labelstudio.json'
        
        # Caminho completo para salvar o arquivo na pasta de saída
        output_path = os.path.join(self.OUTPUT_FOLDER, output_filename)
        
        with open(output_path, 'w', encoding='utf-8') as out:
            json.dump(self.dataset, out, ensure_ascii=False, indent=4)
        
        self._dataset_status = DatasetStatus.RELEASED
        logger.info(f'Dataset {self.dataset_file} exportado para {output_filename} na pasta output. Status: {self._dataset_status}.')

def main():
    DATA_FILE_NAME = sys.argv[1]
    LabelStudioProcessor(DATA_FILE_NAME).to_label_studio_format().export_dataset()
    
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
