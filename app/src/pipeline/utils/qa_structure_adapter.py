import json
from functools import reduce

# Carregar o JSON do arquivo
with open('final-project.series.json', 'r', encoding='utf-8') as file:
    json_data = json.load(file)

# Campos desejados
desired_fields = ["Data_Reclamacao", "Órgão", "Local", "Setor", "Descrição", "Status", "Data_Resolucao"]

class JSONAdapter:
    def __init__(self, json_data):
        self.data = json_data if isinstance(json_data, list) else []
    
    def get_filtered_data(self, fields):
        def extract_fields(entry):
            return {field: entry.get(field, None) for field in fields}
        
        return [extract_fields(entry) for entry in self.data]

if __name__ == '__main__':
    adapter = JSONAdapter(json_data)
    filtered_data = adapter.get_filtered_data(desired_fields)
    print(json.dumps(filtered_data, indent=4, ensure_ascii=False))
