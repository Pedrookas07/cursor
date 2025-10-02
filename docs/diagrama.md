# Diagrama do Sistema de Vigilância Rebuss

Este arquivo apresenta dois diagramas Mermaid: o fluxo principal de processamento e a visão de componentes do sistema.

## Fluxo Principal

```mermaid
flowchart TD
    subgraph Slack
        S["Canal leitura: #desarrollo"]
        R["Canal resposta: #monitor-inventarios"]
    end

    Env[".env: SLACK_BOT_TOKEN"] --> Get
    Env --> Send

    S -->|conversations.history| Get["get_latest_messages()"]
    Get --> F{is_log_message?}
    F -- "Não" --> Skip[Ignora mensagem]
    F -- "Sim" --> Parse["parser_rebuss_simples.parse_rebuss_log_simples()"]

    Parse --> Org["create_organized_alert_final()"]
    Org --> Inv["create_inventory_info_block_final()"]
    Org --> Stats["create_statistics_block_final()"]
    Stats --> Hist["conversations.history (7 dias)\nget_error_statistics()"]
    Org --> Ctx["RebussContextualizer.create_contextualization_block()"]
    Org --> An["create_analysis_block_final()"]
    Org --> Sol["create_solutions_block_final()"]
    Org --> Send["send_organized_alert_final()"]

    Send -->|chat.postMessage| R

    classDef api fill:#eef,stroke:#88a;
    classDef mod fill:#efe,stroke:#8a8;
    class Get,Send,Hist api;
    class Parse,Inv,Stats,Ctx,An,Sol mod;
```

## Visão de Componentes

```mermaid
graph LR
    A["SistemaFinalIntegrado\n(sistema_final_integrado.py)"]
    P["parse_rebuss_simples\n(parser_rebuss_simples.py)"]
    C["RebussContextualizer\n(contextualizador_rebuss.py)"]
    ENV["dotenv / .env"]
    API[("Slack Web API\n(conversations.history / chat.postMessage)")]
    CH["Canais Slack\n#desarrollo / #monitor-inventarios"]

    ENV --> A
    CH --> A
    A -->|usa| P
    A -->|usa| C
    A -.->|HTTP| API
    A -->|POST| API
    API -->|entrega| CH

    style API fill:#eef,stroke:#88a
    style ENV fill:#ffd,stroke:#aa8
```

---

Notas rápidas
- Loop contínuo: `start_monitoring()` chama `process_new_messages()` a cada 30s.
- Estatísticas: `get_error_statistics()` consulta o histórico de 7 dias no Slack.
- Contexto: `RebussContextualizer` infere controller/action e intenção do usuário.

