# 🤖 API 3C Robot

Este projeto é um robô Python desenvolvido para sincronizar dados de chamadas de uma API 3C (FluxoTI) com um banco de dados SQL Server. Ele foi projetado para operar de forma agendada ou manual, coletando informações detalhadas sobre chamadas e dados de mailing, e registrando o histórico de suas execuções.

## ✨ Funcionalidades

*   **Coleta de Dados da API 3C**: Busca dados de chamadas de campanhas específicas da API 3C, com paginação para lidar com grandes volumes de dados.
*   **Sincronização com SQL Server**: Salva os dados coletados em tabelas dedicadas (`calls`, `mailing_data`, `execution_logs`) em um banco de dados SQL Server.
*   **Gerenciamento de Conexão com Banco de Dados**: Testa e gerencia a conexão com o SQL Server, garantindo a integridade dos dados.
*   **Criação Automática de Tabelas**: Verifica e cria as tabelas necessárias no banco de dados se elas não existirem.
*   **Modos de Execução**:
    *   **Agendado (Scheduled)**: Executa a sincronização diariamente em um horário configurável via expressão CRON.
    *   **Manual**: Permite a execução única para o dia anterior ou para um período específico com campanhas definidas.
*   **Sistema de Logging Robusto**: Utiliza `logging` com rotação de arquivos para registrar eventos, informações e erros, facilitando o monitoramento e depuração.
*   **Tratamento de Erros**: Inclui tratamento de erros para requisições de API, operações de banco de dados e problemas de conexão.
*   **Geração de Executável**: Pode ser compilado em um executável autônomo usando PyInstaller.

## 🚀 Tecnologias Utilizadas

*   **Python 3.x**
*   **`requests`**: Para fazer requisições HTTP à API.
*   **`pyodbc`**: Para conexão e interação com o banco de dados SQL Server.
*   **`schedule`**: Para agendamento de tarefas em modo `scheduled`.
*   **`python-dotenv`**: Para carregar variáveis de ambiente de um arquivo `.env`.
*   **`PyInstaller`**: Para empacotar a aplicação em um executável.

## 📋 Pré-requisitos

Antes de começar, certifique-se de ter:

*   **Python 3.x** instalado.
*   **Driver ODBC para SQL Server**: Necessário para a conexão `pyodbc`. Você pode baixá-lo no site da Microsoft (ex: ODBC Driver 17 for SQL Server).
*   **Acesso a um banco de dados SQL Server**.
*   **Credenciais da API 3C (MANAGER_TOKEN)**.

## ⚙️ Configuração do Ambiente

### Variáveis de Ambiente (`.env`)

Crie um arquivo chamado `.env` na raiz do projeto (ou copie o `.env.example` e renomeie) e configure as seguintes variáveis:

```dotenv
# Configurações da API 3C
MANAGER_TOKEN="SEU_TOKEN_DA_API_3C"
BASE_URL="http://app.3c.fluxoti.com.br/api/v1/calls" # URL base da API (pode ser alterada se necessário)
PER_PAGE=100 # Número de registros por página na consulta da API

# Configurações do Banco de Dados SQL Server
DB_SERVER="SEU_IP_OU_HOST_DO_BANCO,PORTA"
DB_DATABASE="SEU_NOME_DO_BANCO"
DB_USERNAME="SEU_USUARIO_DO_BANCO"
DB_PASSWORD="SUA_SENHA_DO_BANCO"
DB_DRIVER="ODBC Driver 17 for SQL Server"

# Configurações de Logging
LOG_LEVEL="INFO" # Nível de log (DEBUG, INFO, WARNING, ERROR, CRITICAL)

# Configurações de Execução
EXECUTION_MODE="scheduled" # ou "manual"
CRON_SCHEDULE="0 2 * * *" # Expressão CRON para modo agendado (Ex: "0 2 * * *" para 02:00 AM todos os dias)

# Parâmetros para EXECUTION_MODE="manual" (opcional)
# Se não forem definidos, o modo manual sincronizará o dia anterior.
# MANUAL_START_DATE="YYYY-MM-DD HH:MM:SS" # Ex: 2023-01-01 00:00:00
# MANUAL_END_DATE="YYYY-MM-DD HH:MM:SS" # Ex: 2023-01-01 23:59:59
# MANUAL_CAMPAIGN_IDS="5,6" # IDs das campanhas separados por vírgula
```

## 📦 Instalação

1.  **Clone o repositório:**
    ```bash
    git clone https://github.com/seu-usuario/API3CRobot.git
    cd API3CRobot
    ```
2.  **Crie e ative um ambiente virtual (recomendado):**
    ```bash
    python -m venv venv
    # No Windows
    .\venv\Scripts\activate
    # No macOS/Linux
    source venv/bin/activate
    ```
3.  **Instale as dependências:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Como Rodar em Desenvolvimento

Certifique-se de que seu arquivo `.env` esteja configurado corretamente.

### Modo Agendado (Scheduled)

Para rodar o robô em modo agendado, ele verificará a cada minuto se é hora de executar a sincronização diária (baseado na variável `CRON_SCHEDULE` do `.env`).

1.  Defina `EXECUTION_MODE="scheduled"` no seu arquivo `.env`.
2.  Execute o script principal:
    ```bash
    python app.py
    ```
    O robô iniciará e aguardará o horário configurado para a execução. Para pará-lo, pressione `Ctrl+C`.

### Modo Manual

Para rodar o robô uma única vez.

1.  Defina `EXECUTION_MODE="manual"` no seu arquivo `.env`.
2.  Você pode configurar `MANUAL_START_DATE`, `MANUAL_END_DATE` e `MANUAL_CAMPAIGN_IDS` no `.env` para sincronizar um período específico. Se não configurados, ele sincronizará os dados do dia anterior.
3.  Execute o script principal:
    ```bash
    python app.py
    ```
    O robô executará a sincronização e finalizará.

## 🛠️ Como Compilar para Produção (PyInstaller)

Para criar um executável autônomo do robô, você pode usar o PyInstaller.

1.  **Instale o PyInstaller** (se ainda não tiver):
    ```bash
    pip install pyinstaller
    ```
2.  **Compile o projeto:**
    O arquivo `app.spec` já está configurado para incluir o `.env` e criar um executável `onefile` (arquivo único) para console.
    ```bash
    pyinstaller app.spec
    ```
    Este comando criará um diretório `dist` na raiz do projeto, contendo o executável `app.exe` (no Windows) ou `app` (no Linux/macOS).
3.  **Executar o aplicativo compilado:**
    Navegue até o diretório `dist/app` (ou `dist` se o nome do executável for `app.exe` diretamente) e execute o arquivo.
    ```bash
    # No Windows
    .\dist\app\app.exe
    # No macOS/Linux
    ./dist/app/app
    ```
    Certifique-se de que o arquivo `.env` esteja presente no mesmo diretório do executável compilado para que as configurações sejam carregadas corretamente.

## 🗄️ Estrutura do Banco de Dados

O robô cria e utiliza as seguintes tabelas no SQL Server:

### `calls`

Armazena os dados detalhados de cada chamada coletada da API.

| Coluna                       | Tipo           | Descrição                                     |
| :--------------------------- | :------------- | :-------------------------------------------- |
| `id`                         | `NVARCHAR(50)` | ID único da chamada (PK)                      |
| `list_name`                  | `NVARCHAR(255)`| Nome da lista de chamadas                     |
| `number`                     | `NVARCHAR(50)` | Número de telefone da chamada                 |
| `call_date`                  | `DATETIME`     | Data e hora da chamada                        |
| `call_date_rfc3339`          | `NVARCHAR(50)` | Data e hora da chamada no formato RFC3339     |
| `campaign_id`                | `INT`          | ID da campanha                                |
| `campaign`                   | `NVARCHAR(255)`| Nome da campanha                              |
| `queue_id`                   | `NVARCHAR(50)` | ID da fila                                    |
| `queue_name`                 | `NVARCHAR(255)`| Nome da fila                                  |
| `ring_group_id`              | `NVARCHAR(50)` | ID do grupo de toque                          |
| `ring_group_name`            | `NVARCHAR(255)`| Nome do grupo de toque                        |
| `ivr_name`                   | `NVARCHAR(255)`| Nome do IVR                                   |
| `receptive_name`             | `NVARCHAR(255)`| Nome do receptivo                             |
| `receptive_phone`            | `NVARCHAR(50)` | Telefone do receptivo                         |
| `receptive_did`              | `NVARCHAR(50)` | DID do receptivo                              |
| `has_agent`                  | `BIT`          | Indica se houve agente na chamada             |
| `agent`                      | `NVARCHAR(255)`| Nome do agente                                |
| `acw_time`                   | `NVARCHAR(20)` | Tempo de ACW (After Call Work)                |
| `speaking_time`              | `NVARCHAR(20)` | Tempo de fala                                 |
| `ivr_time`                   | `NVARCHAR(20)` | Tempo no IVR                                  |
| `ivr_after_call_time`        | `NVARCHAR(20)` | Tempo no IVR após a chamada                   |
| `amd_time`                   | `NVARCHAR(20)` | Tempo de AMD (Answering Machine Detection)    |
| `waiting_time`               | `NVARCHAR(20)` | Tempo de espera                               |
| `speaking_with_agent_time`   | `NVARCHAR(20)` | Tempo de conversação com agente               |
| `route_id`                   | `INT`          | ID da rota                                    |
| `route_name`                 | `NVARCHAR(255)`| Nome da rota                                  |
| `route_host`                 | `NVARCHAR(255)`| Host da rota                                  |
| `route_endpoint`             | `NVARCHAR(500)`| Endpoint da rota                              |
| `route_caller_id`            | `NVARCHAR(50)` | Caller ID da rota                             |
| `billed_time`                | `NVARCHAR(20)` | Tempo faturado                                |
| `billed_value`               | `NVARCHAR(50)` | Valor faturado                                |
| `qualification`              | `NVARCHAR(255)`| Qualificação da chamada                       |
| `behavior`                   | `NVARCHAR(255)`| Comportamento da chamada                      |
| `readable_behavior_text`     | `NVARCHAR(500)`| Texto legível do comportamento                |
| `phone_type`                 | `NVARCHAR(50)` | Tipo de telefone                              |
| `recording`                  | `NVARCHAR(500)`| URL da gravação                               |
| `recording_amd`              | `NVARCHAR(500)`| URL da gravação AMD                           |
| `status_id`                  | `INT`          | ID do status da chamada                       |
| `readable_status_text`       | `NVARCHAR(500)`| Texto legível do status                       |
| `readable_amd_status_text`   | `NVARCHAR(500)`| Texto legível do status AMD                   |
| `mode`                       | `NVARCHAR(50)` | Modo da chamada                               |
| `hangup_cause`               | `INT`          | Causa do desligamento                        |
| `sip_cause`                  | `NVARCHAR(20)` | Causa SIP                                     |
| `readable_hangup_cause_text` | `NVARCHAR(500)`| Texto legível da causa de desligamento        |
| `feedback`                   | `NVARCHAR(MAX)`| Feedback da chamada                           |
| `recorded`                   | `BIT`          | Indica se a chamada foi gravada               |
| `ended_by_agent`             | `BIT`          | Indica se a chamada foi encerrada pelo agente |
| `qualification_note`         | `NVARCHAR(MAX)`| Nota de qualificação                          |
| `sid`                        | `NVARCHAR(255)`| SID da chamada                                |
| `is_dmc`                     | `BIT`          | É DMC?                                        |
| `is_unknown`                 | `BIT`          | É desconhecido?                               |
| `is_transferred`             | `BIT`          | Foi transferida?                              |
| `is_consult`                 | `BIT`          | É consulta?                                   |
| `is_transfer`                | `BIT`          | É transferência?                              |
| `is_conversion`              | `BIT`          | É conversão?                                  |
| `qualification_id`           | `INT`          | ID da qualificação                            |
| `consult_cancelled`          | `BIT`          | Consulta cancelada?                           |
| `recording_transfer`         | `NVARCHAR(500)`| Gravação da transferência                     |
| `recording_consult`          | `NVARCHAR(500)`| Gravação da consulta                          |
| `recording_after_consult_cancel` | `NVARCHAR(500)`| Gravação após cancelamento de consulta        |
| `ivr_digit_pressed`          | `NVARCHAR(50)` | Dígito IVR pressionado                        |
| `record_name`                | `NVARCHAR(255)`| Nome do registro                              |
| `transcription`              | `NVARCHAR(MAX)`| Transcrição da chamada                        |
| `ai_evaluation_status`       | `NVARCHAR(255)`| Status da avaliação por IA                    |
| `created_at`                 | `DATETIME`     | Data de criação do registro                   |
| `updated_at`                 | `DATETIME`     | Data da última atualização do registro        |

### `mailing_data`

Armazena dados adicionais de mailing associados às chamadas.

| Coluna              | Tipo           | Descrição                                     |
| :------------------ | :------------- | :-------------------------------------------- |
| `id`                | `INT`          | ID único (PK, auto-incremento)                |
| `_id`               | `NVARCHAR(50)` | ID interno do mailing                         |
| `call_id`           | `NVARCHAR(50)` | Chave estrangeira para `calls.id`             |
| `identifier`        | `NVARCHAR(50)` | Identificador do mailing                      |
| `campaign_id`       | `INT`          | ID da campanha                                |
| `company_id`        | `INT`          | ID da empresa                                 |
| `list_id`           | `INT`          | ID da lista                                   |
| `uf`                | `NVARCHAR(10)` | UF                                            |
| `phone`             | `NVARCHAR(50)` | Telefone                                      |
| `dialed_phone`      | `INT`          | Telefone discado                              |
| `dialed_identifier` | `INT`          | Identificador discado                         |
| `on_calling`        | `INT`          | Em chamada                                    |
| `column_position`   | `INT`          | Posição da coluna                             |
| `row_position`      | `INT`          | Posição da linha                              |
| `estrategia`        | `NVARCHAR(255)`| Estratégia                                    |
| `razao_social`      | `NVARCHAR(255)`| Razão Social                                  |
| `nome_fantasia`     | `NVARCHAR(255)`| Nome Fantasia                                 |
| `valor_conta`       | `NVARCHAR(100)`| Valor da Conta                                |
| `cidade`            | `NVARCHAR(255)`| Cidade                                        |
| `cep`               | `NVARCHAR(20)` | CEP                                           |
| `uf_mailing`        | `NVARCHAR(10)` | UF do Mailing                                 |
| `socio`             | `NVARCHAR(255)`| Sócio                                         |
| `created_at`        | `DATETIME`     | Data de criação do registro                   |
| `updated_at`        | `DATETIME`     | Data da última atualização do registro        |

### `execution_logs`

Registra o histórico de execuções do robô.

| Coluna                 | Tipo            | Descrição                                     |
| :--------------------- | :-------------- | :-------------------------------------------- |
| `id`                   | `INT`           | ID único (PK, auto-incremento)                |
| `execution_date`       | `DATETIME`      | Data e hora do início da execução             |
| `start_date`           | `NVARCHAR(50)`  | Data de início do período consultado          |
| `end_date`             | `NVARCHAR(50)`  | Data de fim do período consultado             |
| `campaign_ids`         | `NVARCHAR(100)` | IDs das campanhas consultadas                 |
| `total_records`        | `INT`           | Total de registros processados                |
| `successful_records`   | `INT`           | Total de registros salvos com sucesso         |
| `failed_records`       | `INT`           | Total de registros com falha                  |
| `execution_time_seconds` | `INT`           | Tempo total de execução em segundos           |
| `status`               | `NVARCHAR(20)`  | Status da execução (RUNNING, COMPLETED_SUCCESS, COMPLETED_WITH_ERRORS, FAILED, COMPLETED_NO_DATA) |
| `error_message`        | `NVARCHAR(MAX)` | Mensagem de erro, se houver                   |
| `created_at`           | `DATETIME`      | Data de criação do registro                   |

## 📄 Logs

O robô gera arquivos de log no diretório `logs/` na raiz do projeto.

*   `api_robot_main.log`: Contém logs detalhados de todas as operações (nível DEBUG e superior).
*   `api_robot_errors.log`: Contém apenas logs de erro (nível ERROR e superior).

Os logs são rotacionados automaticamente para evitar que os arquivos cresçam demais.