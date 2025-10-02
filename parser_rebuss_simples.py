#!/usr/bin/env python3
"""Parser simples para logs do sistema Rebuss - sem emojis"""

import re
import json
from datetime import datetime

def parse_rebuss_log_simples(log_entry):
    """Parser simples para logs Rebuss"""
    
    parsed_data = {
        "app": None,
        "error": None,
        "timestamp": None,
        "inventory_id": None,
        "inventory_name": None,
        "location": None,
        "user": None,
        "url": None,
        "error_msg": None,
        "request_params": None
    }

    # Extract App, Error Code, and Timestamp from the header
    # Padr?o original: Counter error 500 [2025-09-27 16:55:42]
    # Padr?o com markdown: *Counter error 500 [2025-09-28 04:08:55]*
    match_header = re.search(r"\*(Counter|Admin|APP)\s+error\s+(\d{3})\s+\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]\*", log_entry)
    if match_header:
        parsed_data["app"] = match_header.group(1)
        parsed_data["error"] = match_header.group(2)
        parsed_data["timestamp"] = match_header.group(3)
    else:
        # Tentar padr?o sem markdown
        match_header = re.search(r"^(Counter|Admin|APP)\s+error\s+(\d{3})\s+\[(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2}:\d{2})\]", log_entry)
        if match_header:
            parsed_data["app"] = match_header.group(1)
            parsed_data["error"] = match_header.group(2)
            parsed_data["timestamp"] = match_header.group(3)

    # Extract Inventory ID, Name, and Location (apenas para Counter)
    # Formato: 44998 - Assai Atacadista 337  BARUERI AVENIDA DO CAFE  SP 2025-09-30 (Sergipe)
    if parsed_data.get("app") == "Counter":
        match_inventory_info = re.search(r"(\d+)\s+-\s+([^(]+)\s+\((\w+)\)", log_entry)
        if match_inventory_info:
            parsed_data["inventory_id"] = match_inventory_info.group(1)
            parsed_data["inventory_name"] = match_inventory_info.group(2).strip()
            parsed_data["location"] = match_inventory_info.group(3).strip()
    elif parsed_data.get("app") == "Admin":
        # Para Admin, n?o h? invent?rio espec?fico - ? o sistema de administra??o
        parsed_data["inventory_id"] = None
        parsed_data["inventory_name"] = "Sistema de Administra??o"
        parsed_data["location"] = "Sistema Admin"

    # Extract Request User (Operador)
    match_request_user = re.search(r"Request:\s*\n([^\n]+)", log_entry, re.DOTALL)
    if match_request_user:
        user_line = match_request_user.group(1).strip()
        # Para Admin, pode ter IP na primeira linha e usu?rio na segunda
        if re.match(r"^\(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\)$", user_line):
            # Se a primeira linha ? IP, buscar a pr?xima linha para o usu?rio
            lines = log_entry.split('\n')
            for i, line in enumerate(lines):
                if line.strip() == user_line:
                    if i + 1 < len(lines):
                        next_line = lines[i + 1].strip()
                        if not next_line.startswith('<') and not next_line.startswith('{') and not next_line.startswith('http'):
                            parsed_data["user"] = next_line
                            break
        elif not user_line.startswith('<') and not user_line.startswith('{'):
            parsed_data["user"] = user_line

    # Extract Request URL
    match_request_url = re.search(r"http[s]?:\/\/[^\s]+", log_entry)
    if match_request_url:
        parsed_data["url"] = match_request_url.group(0)

    # Extract Request Parameters (JSON)
    match_request_params = re.search(r"(\{.*?\})", log_entry, re.DOTALL)
    if match_request_params:
        parsed_data["request_params"] = match_request_params.group(1)

    # Extract Error Message
    match_error_message = re.search(r"Error:\s*\n(.*?)(?:\n\s*Source:|\n\s*Backtrace:|$)", log_entry, re.DOTALL)
    if match_error_message:
        error_text = match_error_message.group(1).strip()
        parsed_data["error_msg"] = error_text

    return parsed_data

def create_inventory_info_block_simples(log_entry):
    """Cria bloco com informa??es do invent?rio - formato simples"""
    
    app = log_entry.get('app', 'UNKNOWN')
    error = log_entry.get('error', 'UNKNOWN')
    inventory_id = log_entry.get('inventory_id', 'N/A')
    inventory_name = log_entry.get('inventory_name', 'N/A')
    user = log_entry.get('user', 'N/A')
    url = log_entry.get('url', 'N/A')
    location = log_entry.get('location', 'N/A')
    timestamp = datetime.now().strftime('%H:%M:%S')
    
    # Criar bloco baseado no tipo de app
    if app == "Admin":
        # Para Admin, n?o h? invent?rio espec?fico
        block = f"""SISTEMA E LOG
```
{timestamp} | {inventory_name} ({location})
{user} | {location}
{app} Error {error}
{url}
```"""
    else:
        # Para Counter, usar hyperlink do invent?rio
        inventory_link = f"<https://admin.rebuss.com/inventories/{inventory_id}/|{inventory_id} - {inventory_name}>"
        block = f"""INVENTARIO E LOG
```
{timestamp} | {inventory_link} ({location})
{user} | {location}
{app} Error {error}
{url}
```"""
    
    return block

def test_parser_simples():
    """Testa o parser simples"""
    
    print("=== TESTE PARSER SIMPLES ===")
    
    # Log de exemplo Counter
    test_log_counter = """Counter error 500 [2025-09-27 16:55:42]
44998 - Assai Atacadista 337  BARUERI AVENIDA DO CAFE  SP 2025-09-30 (Sergipe)
 Request:
Danilo Silva dos Santos
http://localhost/capturas/perform_copy_from_reader.json
{"importacion"=>"automatica", "controller"=>"capturas", "action"=>"perform_copy_from_reader", "format"=>"json"}
 Error:
undefined method `split' for nil:NilClass
 Source:
no-source
 Backtrace:
/var/counter-app/app/controllers/capturas_controller.rb:215:in `block in perform_copy_from_reader'
/var/counter-app/app/controllers/capturas_controller.rb:157:in `each'
/var/counter-app/app/controllers/capturas_controller.rb:157:in `each_with_index'
/var/counter-app/app/controllers/capturas_controller.rb:157:in `perform_copy_from_reader'"""

    # Log de exemplo Admin
    test_log_admin = """Admin error 404 [2025-09-27 00:36:40]
Request:
(107.209.92.255)
Kamran Abolhassani
https://admin.rebuss.com/inventories/41995
<ActionController::Parameters {"_method"=>"delete", "authenticity_token"=>"OLTD3DNrtpsDz7uzTYAt2Z7dStSKRxEqQQ1X/2WeKSKPGeES0H6qeZ8P97jzB7Ed8v3N6ygsFfuPA+aebCKYMw==", "controller"=>"inventories", "action"=>"destroy", "id"=>"41995"} permitted: false>
 Error:
Couldn't find Inventory with 'id'=41995
 Backtrace:
/mnt/app/releases/20250924210152/app/controllers/inventories_controller.rb:482:in `set_inventory'"""

    # Testar Counter
    print("\n--- TESTE COUNTER ---")
    parsed_counter = parse_rebuss_log_simples(test_log_counter)
    
    print("DADOS EXTRAIDOS COUNTER:")
    for key, value in parsed_counter.items():
        print(f"  {key}: {value}")
    
    print("\nBLOCO COUNTER CRIADO:")
    inventory_block_counter = create_inventory_info_block_simples(parsed_counter)
    print(inventory_block_counter)
    
    # Testar Admin
    print("\n--- TESTE ADMIN ---")
    parsed_admin = parse_rebuss_log_simples(test_log_admin)
    
    print("DADOS EXTRAIDOS ADMIN:")
    for key, value in parsed_admin.items():
        print(f"  {key}: {value}")
    
    print("\nBLOCO ADMIN CRIADO:")
    inventory_block_admin = create_inventory_info_block_simples(parsed_admin)
    print(inventory_block_admin)
    
    print("\n" + "="*50)
    print("SUCCESS: Parser simples funcionando para Counter e Admin!")

if __name__ == "__main__":
    test_parser_simples()
