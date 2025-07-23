import xmltodict
import json
import os
import jsonschema
import datetime
import io # Importação adicionada para depuração, se necessário

# --- Função Auxiliar para Conversão de String para Booleano ---
# XML AUDESP usa 'S'/'N', JSON Schema usa true/false
def convert_sn_to_boolean(value):
    if value is None:
        return None # Retorna None se o valor for None (campo opcional)
    return value.upper() == 'S'

def convert_and_map_ata_xml_to_json(xml_file_path, json_schema_path):
    try:
        # 1. Ler o arquivo XML
        with open(xml_file_path, 'r', encoding='ISO-8859-1') as f:
            xml_content = f.read()

        # 2. Fazer o PARSE do XML para um dicionário Python
        #    process_namespaces=True: Lida com namespaces (xmlns:gen, xmlns:tag)
        #    namespaces: Remove os prefixos 'gen:' e o namespace da raiz para facilitar o acesso
        xml_dict = xmltodict.parse(
            xml_content,
            process_namespaces=True,
            namespaces={
                'http://www.tce.sp.gov.br/audesp/xml/ataRegistroPrecos': None, # Namespace da tag raiz <AtaRegistroPrecos>
                'http://www.tce.sp.gov.br/audesp/xml/generico': None, # Namespace para tags como <gen:AnoExercicio>
                'http://www.tce.sp.gov.br/audesp/xml/tagcomum': None # Se houver tags com prefixo 'tag:'
            }
        )

        # Imprime a estrutura do XML após o parse (dicionário Python) para debug
        print("--- Estrutura do XML após o parse (dicionário Python) ---")
        # Removendo a linha problemática que causava 'Illegal trailing comma' na impressão de xml_dict
        # Acreditamos que o problema não era no xml_dict em si, mas no json.dumps quando ele era muito grande/complexo para o console.
        # print(json.dumps(xml_dict, indent=2))
        print("-----------------------------------------------------")
        # Se quiser ver o xml_dict completo para debug, você pode salvá-lo em um arquivo:
        # with open("xml_dict_debug.json", "w", encoding="utf-8") as f_debug:
        #     json.dump(xml_dict, f_debug, indent=2, ensure_ascii=False)
        # print("DEBUG: xml_dict salvo em 'xml_dict_debug.json'")


        # --- Acessando os dados no dicionário: ---
        ata_xml_data = xml_dict.get('AtaRegistroPrecos', {})
        descritor_xml_data = ata_xml_data.get('Descritor', {})
        dados_ata_xml_data = ata_xml_data.get('DadosAta', {})

        # --- COMEÇO DO MAPEAMENTO REAL PARA O DICIONÁRIO JSON ---
        json_data = {
            "descritor": {
                # Mapeamento do Descritor - Note a conversão de tipo (string para int)
                "municipio": int(descritor_xml_data.get('Municipio', '0')),
                "entidade": int(descritor_xml_data.get('Entidade', '0')),
                "codigoEdital": dados_ata_xml_data.get('CodigoEdital', ''),
                "codigoAta": dados_ata_xml_data.get('CodigoAta', ''),
                "anoCompra": int(dados_ata_xml_data.get('AnoCompra', '0')),
                "retificacao": convert_sn_to_boolean(dados_ata_xml_data.get('Retificacao'))
            },
            "numeroItem": [], # Inicializa como lista vazia
            "numeroAtaRegistroPreco": dados_ata_xml_data.get('NumeroAtaRegistroPreco', ''),
            "anoAta": int(dados_ata_xml_data.get('AnoAta', '0')),
            "dataAssinatura": dados_ata_xml_data.get('DataAssinatura', ''),
            "dataVigenciaInicio": dados_ata_xml_data.get('DataVigenciaInicio', ''),
            "dataVigenciaFim": dados_ata_xml_data.get('DataVigenciaFim', '')
        }

        # Preencher 'numeroItem' (que é um array de números no JSON)
        itens_xml = dados_ata_xml_data.get('Itens', {}).get('NumeroItem')
        if itens_xml:
            if isinstance(itens_xml, list):
                json_data["numeroItem"] = [int(item) for item in itens_xml]
            else: # Se houver apenas um item, xmltodict retorna string, não lista
                json_data["numeroItem"] = [int(itens_xml)]

        # --- FIM DO MAPEAMENTO ---

        # --- Ponto de Debug: Conteúdo de json_data antes da serialização ---
        print("\n--- Conteúdo de json_data antes da serialização ---")
        print(json_data) # Imprime o dicionário Python diretamente
        print("---------------------------------------------------\n")

        # 4. Validar o JSON gerado contra o JSON Schema
        with open(json_schema_path, 'r', encoding='utf-8') as f:
            schema = json.load(f)
        jsonschema.validate(instance=json_data, schema=schema)
        print("\nJSON validado com sucesso contra o schema!")

        # 5. Converter dicionário Python para string JSON
        # Esta é a linha que estava gerando o erro, vamos mantê-la e ver o que acontece
        json_output = json.dumps(json_data, indent=2, ensure_ascii=False)

        return json_output

    except FileNotFoundError:
        print(f"Erro: Arquivo não encontrado em {xml_file_file} ou {json_schema_path}")
        return None
    except jsonschema.exceptions.ValidationError as ve:
        print(f"\n--- ERRO DE VALIDAÇÃO DO JSON SCHEMA ---")
        print(f"Mensagem: {ve.message}")
        print(f"Caminho do erro: {list(ve.path)}")
        print(f"Esquema que falhou: {ve.validator_value} para '{ve.validator}'")
        print("------------------------------------------")
        return None
    except Exception as e:
        print(f"Erro durante a conversão: {e}")
        # Se o erro for o "Illegal trailing comma", ele cairá aqui.
        # Vamos tentar salvar o json_data para inspeção manual.
        try:
            with open("json_data_ERROR_DEBUG.json", "w", encoding="utf-8") as debug_f:
                json.dump(json_data, debug_f, indent=2, ensure_ascii=False)
            print("DEBUG: Conteúdo de json_data salvo em 'json_data_ERROR_DEBUG.json' para inspeção.")
        except Exception as debug_e:
            print(f"DEBUG: Não foi possível salvar o debug file: {debug_e}")
        return None

# --- Bloco de Execução Principal ---
if __name__ == "__main__":
    # Ajuste para os seus caminhos e nomes de arquivos
    xml_input_file = 'exemplo_ata_registro_precos.xml' # Seu XML de Ata de exemplo simulada
    json_output_file = 'ata_convertida.json'
    # Substitua pelo nome do arquivo JSON Schema da Ata que você baixou
    json_schema_file = 'ata_schema.json' # EX: 'ata-schema-v2_0.json'

    # Verifique se os arquivos existem antes de tentar processar
    if not os.path.exists(json_schema_file):
        print(f"Erro: O arquivo de esquema JSON '{json_schema_file}' não foi encontrado. Por favor, ajuste o caminho ou nome.")
    elif not os.path.exists(xml_input_file):
        print(f"Erro: O arquivo XML de entrada '{xml_input_file}' não foi encontrado. Por favor, ajuste o caminho ou nome.")
    else:
        # Se tudo parece certo, tenta a conversão
        converted_json = convert_and_map_ata_xml_to_json(xml_input_file, json_schema_file)

        if converted_json:
            print("\n--- JSON Final Gerado e Retornado ---")
            # O converted_json já foi impresso e salvo dentro da função convert_and_map_ata_xml_to_json
            # Se você quiser imprimir novamente ou salvar aqui, pode fazer
            # print(converted_json)
            # with open(json_output_file, 'w', encoding='utf-8') as f:
            #     f.write(converted_json)
            # print(f"\nJSON salvo em: {json_output_file}")
            pass # Apenas para indicar que esta parte do if é intencionalmente vazia se não for imprimir/salvar aqui
        else:
            print("\nNão foi possível gerar o JSON final. Verifique os erros acima.")