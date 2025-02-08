import os
import json
import sys
import logging

logger = logging.getLogger(__name__)

class JSONAdapter:
    def __init__(self, data):
        self.data = data
    
    def get_filtered_data(self, fields):
        return {field: self.data.get(field, None) for field in fields}

class QuestionAnswerFormatter:
    DATA_FOLDER = '/home/luan/Documentos/Trabalho_Final_BD/dataset/output/'
    OUTPUT_FOLDER = os.path.join(DATA_FOLDER, 'output-dataset-transformed') 
    
    def __init__(self, dataset_path):
        self.dataset_name, ext = os.path.splitext(dataset_path)
        dataset_full_path = os.path.join(self.DATA_FOLDER, dataset_path)  # Usando os.path.join
        try:
            with open(dataset_full_path, encoding='utf-8') as file:
                self.dataset = json.load(file)
        except FileNotFoundError:
            logger.error(f"Arquivo não encontrado: {dataset_full_path}")
            sys.exit(1)
        except json.JSONDecodeError:
            logger.error(f"Erro ao decodificar o arquivo JSON: {dataset_full_path}")
            sys.exit(1)
        
        self._fields_schema = ["Data_Reclamacao", "Órgão", "Local", "Setor", "Descrição", "Status", "Data_Resolucao"]
    
    def extract_fields(self):
        logger.info('Extraindo campos do dataset usando o schema definido.')
        _tmp_dataset = [JSONAdapter(data).get_filtered_data(self._fields_schema) for data in self.dataset]
        self.dataset = _tmp_dataset.copy()
        del _tmp_dataset
        logger.info('Campos extraídos com sucesso.')
        return self
    
    def export_dataset(self):
        os.makedirs(self.OUTPUT_FOLDER, exist_ok=True)

        output_filename = self.dataset_name + '_formatted.json' 
        output_full_path = os.path.join(self.OUTPUT_FOLDER, output_filename)  # Usando os.path.join
        logger.info(f'Exportando dataset formatado para o arquivo: {output_full_path}')

        try:
            with open(output_full_path, 'w', encoding='utf-8') as out:
                json.dump(self.dataset, out, ensure_ascii=False, indent=4)
            logger.info('Exportação concluída com sucesso.')
        except IOError:
            logger.error(f"Erro ao salvar o arquivo: {output_full_path}")
            sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        logger.error('Uso incorreto do script. Exemplo de uso: python src/transform_dataset.py <nome_do_arquivo_dataset>')
        sys.exit(1)

    DATA_FILE_NAME = sys.argv[1]
    logger.info(f'Iniciando o processo de formatação para o arquivo: {DATA_FILE_NAME}')
    QuestionAnswerFormatter(DATA_FILE_NAME).extract_fields().export_dataset()
    logger.info('Processo concluído.')
