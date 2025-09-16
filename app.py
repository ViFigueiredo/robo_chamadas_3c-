import os
import sys
import requests
import pyodbc
import json
import schedule
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from logging.handlers import RotatingFileHandler
from urllib.parse import quote_plus
import traceback
from dotenv import load_dotenv

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()


class DatabaseManager:
    """Gerenciador de conexão e operações de banco de dados"""
    
    def __init__(self, config: Dict[str, str], logger: logging.Logger):
        self.config = config
        self.logger = logger
        self.connection = None
    
    def test_connection(self) -> Tuple[bool, Optional[str]]:
        """
        Testa a conexão com o banco de dados
        Returns: (sucesso: bool, erro: Optional[str])
        """
        self.logger.info("🔌 Iniciando teste de conexão com banco de dados...")
        
        try:
            connection_string = (
                f"DRIVER={{{self.config['driver']}}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            
            self.logger.debug(f"📝 String de conexão: DRIVER={self.config['driver']};SERVER={self.config['server']};DATABASE={self.config['database']};UID={self.config['username']};PWD=***")
            
            test_conn = pyodbc.connect(connection_string)
            
            # Testa uma query simples
            cursor = test_conn.cursor()
            cursor.execute("SELECT 1 as test")
            result = cursor.fetchone()
            cursor.close()
            test_conn.close()
            
            if result and result[0] == 1:
                self.logger.info("✅ Conexão com banco de dados testada com sucesso!")
                return True, None
            else:
                error_msg = "❌ Teste de query falhou - resultado inesperado"
                self.logger.error(error_msg)
                return False, error_msg
                
        except pyodbc.Error as e:
            error_msg = f"❌ Erro de conexão pyodbc: {e}"
            self.logger.error(error_msg)
            return False, error_msg
        except Exception as e:
            error_msg = f"❌ Erro inesperado na conexão: {e}"
            self.logger.error(error_msg)
            return False, error_msg
    
    def get_connection(self):
        """Obtém conexão com o banco de dados"""
        if self.connection is None:
            self.logger.info("🔗 Estabelecendo nova conexão com banco de dados...")
            
            connection_string = (
                f"DRIVER={{{self.config['driver']}}};"
                f"SERVER={self.config['server']};"
                f"DATABASE={self.config['database']};"
                f"UID={self.config['username']};"
                f"PWD={self.config['password']};"
                f"TrustServerCertificate=yes;"
                f"Connection Timeout=30;"
            )
            
            try:
                self.connection = pyodbc.connect(connection_string)
                self.logger.info("✅ Conexão estabelecida com sucesso!")
            except Exception as e:
                self.logger.error(f"❌ Erro ao conectar: {e}")
                raise
        
        return self.connection
    
    def close_connection(self):
        """Fecha conexão com banco de dados"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.logger.info("🔒 Conexão com banco fechada")
            except Exception as e:
                self.logger.error(f"❌ Erro ao fechar conexão: {e}")
    
    def create_tables(self):
        """Cria as tabelas necessárias se não existirem"""
        self.logger.info("🗃️ Verificando e criando tabelas necessárias...")
        
        cursor = self.get_connection().cursor()
        
        try:
            # Tabela principal de chamadas
            self.logger.info("📋 Criando tabela 'calls' se não existir...")
            create_calls_table = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='calls' AND xtype='U')
            BEGIN
                CREATE TABLE calls (
                    id NVARCHAR(50) PRIMARY KEY,
                    list_name NVARCHAR(255),
                    number NVARCHAR(50),
                    call_date DATETIME,
                    call_date_rfc3339 NVARCHAR(50),
                    campaign_id INT,
                    campaign NVARCHAR(255),
                    queue_id NVARCHAR(50),
                    queue_name NVARCHAR(255),
                    ring_group_id NVARCHAR(50),
                    ring_group_name NVARCHAR(255),
                    ivr_name NVARCHAR(255),
                    receptive_name NVARCHAR(255),
                    receptive_phone NVARCHAR(50),
                    receptive_did NVARCHAR(50),
                    has_agent BIT,
                    agent NVARCHAR(255),
                    acw_time NVARCHAR(20),
                    speaking_time NVARCHAR(20),
                    ivr_time NVARCHAR(20),
                    ivr_after_call_time NVARCHAR(20),
                    amd_time NVARCHAR(20),
                    waiting_time NVARCHAR(20),
                    speaking_with_agent_time NVARCHAR(20),
                    route_id INT,
                    route_name NVARCHAR(255),
                    route_host NVARCHAR(255),
                    route_endpoint NVARCHAR(500),
                    route_caller_id NVARCHAR(50),
                    billed_time NVARCHAR(20),
                    billed_value NVARCHAR(50),
                    qualification NVARCHAR(255),
                    behavior NVARCHAR(255),
                    readable_behavior_text NVARCHAR(500),
                    phone_type NVARCHAR(50),
                    recording NVARCHAR(500),
                    recording_amd NVARCHAR(500),
                    status_id INT,
                    readable_status_text NVARCHAR(500),
                    readable_amd_status_text NVARCHAR(500),
                    mode NVARCHAR(50),
                    hangup_cause INT,
                    sip_cause NVARCHAR(20),
                    readable_hangup_cause_text NVARCHAR(500),
                    feedback NVARCHAR(MAX),
                    recorded BIT,
                    ended_by_agent BIT,
                    qualification_note NVARCHAR(MAX),
                    sid NVARCHAR(255),
                    is_dmc BIT,
                    is_unknown BIT,
                    is_transferred BIT,
                    is_consult BIT,
                    is_transfer BIT,
                    is_conversion BIT,
                    qualification_id INT,
                    consult_cancelled BIT,
                    recording_transfer NVARCHAR(500),
                    recording_consult NVARCHAR(500),
                    recording_after_consult_cancel NVARCHAR(500),
                    ivr_digit_pressed NVARCHAR(50),
                    record_name NVARCHAR(255),
                    transcription NVARCHAR(MAX),
                    ai_evaluation_status NVARCHAR(255),
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE()
                )
                PRINT 'Tabela calls criada com sucesso'
            END
            ELSE
            BEGIN
                PRINT 'Tabela calls já existe'
            END
            """
            
            cursor.execute(create_calls_table)
            
            # Tabela de dados de mailing
            self.logger.info("📋 Criando tabela 'mailing_data' se não existir...")
            create_mailing_table = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='mailing_data' AND xtype='U')
            BEGIN
                CREATE TABLE mailing_data (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    _id NVARCHAR(50),
                    call_id NVARCHAR(50),
                    identifier NVARCHAR(50),
                    campaign_id INT,
                    company_id INT,
                    list_id INT,
                    uf NVARCHAR(10),
                    phone NVARCHAR(50),
                    dialed_phone INT,
                    dialed_identifier INT,
                    on_calling INT,
                    column_position INT,
                    row_position INT,
                    estrategia NVARCHAR(255),
                    razao_social NVARCHAR(255),
                    nome_fantasia NVARCHAR(255),
                    valor_conta NVARCHAR(100),
                    cidade NVARCHAR(255),
                    cep NVARCHAR(20),
                    uf_mailing NVARCHAR(10),
                    socio NVARCHAR(255),
                    created_at DATETIME DEFAULT GETDATE(),
                    updated_at DATETIME DEFAULT GETDATE(),
                    FOREIGN KEY (call_id) REFERENCES calls(id) ON DELETE CASCADE
                )
                PRINT 'Tabela mailing_data criada com sucesso'
            END
            ELSE
            BEGIN
                PRINT 'Tabela mailing_data já existe'
            END
            """
            
            cursor.execute(create_mailing_table)
            
            # Tabela de logs de execução
            self.logger.info("📋 Criando tabela 'execution_logs' se não existir...")
            create_logs_table = """
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='execution_logs' AND xtype='U')
            BEGIN
                CREATE TABLE execution_logs (
                    id INT IDENTITY(1,1) PRIMARY KEY,
                    execution_date DATETIME,
                    start_date NVARCHAR(50),
                    end_date NVARCHAR(50),
                    campaign_ids NVARCHAR(100),
                    total_records INT DEFAULT 0,
                    successful_records INT DEFAULT 0,
                    failed_records INT DEFAULT 0,
                    execution_time_seconds INT DEFAULT 0,
                    status NVARCHAR(20) DEFAULT 'RUNNING',
                    error_message NVARCHAR(MAX),
                    created_at DATETIME DEFAULT GETDATE()
                )
                PRINT 'Tabela execution_logs criada com sucesso'
            END
            ELSE
            BEGIN
                PRINT 'Tabela execution_logs já existe'
            END
            """
            
            cursor.execute(create_logs_table)
            
            self.connection.commit()
            self.logger.info("✅ Todas as tabelas foram verificadas/criadas com sucesso!")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar tabelas: {e}")
            self.logger.error(f"📝 Traceback: {traceback.format_exc()}")
            raise
        finally:
            cursor.close()


class LogManager:
    """Gerenciador de logs com múltiplos níveis e rotação"""
    
    @staticmethod
    def setup_logging(log_level: str = "INFO") -> logging.Logger:
        """
        Configura sistema de logging com rotação de arquivos
        """
        # Cria diretório de logs se não existir
        log_dir = "logs"
        if not os.path.exists(log_dir):
            os.makedirs(log_dir)
        
        # Configura logger principal
        logger = logging.getLogger('API3CRobot')
        logger.setLevel(getattr(logging, log_level.upper(), logging.INFO))
        
        # Remove handlers existentes para evitar duplicação
        for handler in logger.handlers[:]:
            logger.removeHandler(handler)
        
        # Formato detalhado para logs
        detailed_formatter = logging.Formatter(
            '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # Formato simples para console
        simple_formatter = logging.Formatter(
            '%(asctime)s | %(levelname)-8s | %(message)s',
            datefmt='%H:%M:%S'
        )
        
        # Handler para arquivo principal com rotação
        main_file_handler = RotatingFileHandler(
            f'{log_dir}/api_robot_main.log',
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        main_file_handler.setLevel(logging.DEBUG)
        main_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(main_file_handler)
        
        # Handler para arquivo de erros
        error_file_handler = RotatingFileHandler(
            f'{log_dir}/api_robot_errors.log',
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        error_file_handler.setLevel(logging.ERROR)
        error_file_handler.setFormatter(detailed_formatter)
        logger.addHandler(error_file_handler)
        
        # Handler para console
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(simple_formatter)
        logger.addHandler(console_handler)
        
        # Log inicial
        logger.info("="*80)
        logger.info("🤖 API 3C Robot - Sistema de Logging Inicializado")
        logger.info(f"📝 Nível de log: {log_level.upper()}")
        logger.info(f"📁 Diretório de logs: {os.path.abspath(log_dir)}")
        logger.info("="*80)
        
        return logger


class API3CRobot:
    def __init__(self):
        """Inicializa o robô com as configurações"""
        # Configura logging
        log_level = os.getenv('LOG_LEVEL', 'INFO')
        self.logger = LogManager.setup_logging(log_level)
        
        self.logger.info("🚀 Inicializando API 3C Robot...")
        
        # Carrega configurações
        self.manager_token = os.getenv('MANAGER_TOKEN')
        self.cron_schedule = os.getenv('CRON_SCHEDULE', '0 2 * * *')  # Padrão: 02:00 todos os dias
        self.per_page = int(os.getenv('PER_PAGE', 100))
        
        self.db_config = {
            'server': os.getenv('DB_SERVER', '192.168.11.200,1434'),
            'database': os.getenv('DB_DATABASE', 'relatorios_discadora_3cmais'),
            'username': os.getenv('DB_USERNAME', 'dbAdmin'),
            'password': os.getenv('DB_PASSWORD', 'Ctelecom2017'),
            'driver': os.getenv('DB_DRIVER', 'ODBC Driver 17 for SQL Server')
        }
        
        # Valida configurações obrigatórias
        if not self.manager_token:
            self.logger.error("❌ MANAGER_TOKEN não encontrado nas variáveis de ambiente")
            raise ValueError("MANAGER_TOKEN é obrigatório")
        
        self.logger.info(f"⚙️ Configurações carregadas:")
        self.logger.info(f"   📅 CRON Schedule: {self.cron_schedule}")
        self.logger.info(f"   📄 Registros por página: {self.per_page}")
        self.logger.info(f"   🗄️ Database Server: {self.db_config['server']}")
        self.logger.info(f"   📊 Database: {self.db_config['database']}")
        self.logger.info(f"   👤 Username: {self.db_config['username']}")
        
        self.base_url = os.getenv('BASE_URL', 'http://app.3c.fluxoti.com.br/api/v1/calls')
        self.logger.info(f"   🔗 Base URL: {self.base_url}")
        
        self.db_manager = DatabaseManager(self.db_config, self.logger)
        
        # Testa conexão inicial
        self.logger.info("🔍 Executando teste inicial de conectividade...")
        success, error = self.db_manager.test_connection()
        if not success:
            self.logger.error(f"❌ Falha no teste de conexão inicial: {error}")
            raise ConnectionError(f"Não foi possível conectar ao banco: {error}")
        
        # Cria tabelas
        try:
            self.db_manager.get_connection()
            self.db_manager.create_tables()
        except Exception as e:
            self.logger.error(f"❌ Erro ao criar tabelas: {e}")
            raise
        finally:
            self.db_manager.close_connection()
    
    def log_execution_start(self, start_date: str, end_date: str, campaign_ids: str) -> int:
        """Registra início da execução e retorna ID do log"""
        self.logger.info(f"📊 Registrando início da execução para período {start_date} até {end_date}")
        
        cursor = self.db_manager.get_connection().cursor()
        try:
            insert_sql = """
            INSERT INTO execution_logs (execution_date, start_date, end_date, campaign_ids, status)
            VALUES (GETDATE(), ?, ?, ?, 'RUNNING')
            """
            cursor.execute(insert_sql, (start_date, end_date, campaign_ids))
            
            # Obtém o ID inserido
            cursor.execute("SELECT @@IDENTITY")
            log_id = cursor.fetchone()[0]
            
            self.db_manager.connection.commit()
            self.logger.info(f"✅ Execução registrada com ID: {log_id}")
            return log_id
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao registrar início da execução: {e}")
            return None
        finally:
            cursor.close()
    
    def log_execution_end(self, log_id: int, total_records: int, successful_records: int, 
                         failed_records: int, execution_time: int, status: str, error_message: str = None):
        """Atualiza log de execução com resultados finais"""
        if log_id is None:
            return
            
        self.logger.info(f"📋 Atualizando log de execução {log_id} com resultados finais")
        
        cursor = self.db_manager.get_connection().cursor()
        try:
            update_sql = """
            UPDATE execution_logs 
            SET total_records = ?, successful_records = ?, failed_records = ?,
                execution_time_seconds = ?, status = ?, error_message = ?
            WHERE id = ?
            """
            cursor.execute(update_sql, (total_records, successful_records, failed_records,
                                      execution_time, status, error_message, log_id))
            
            self.db_manager.connection.commit()
            self.logger.info(f"✅ Log de execução {log_id} atualizado com sucesso")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao atualizar log de execução: {e}")
        finally:
            cursor.close()
    
    def fetch_api_data(self, start_date: str, end_date: str, campaign_ids: str = "5,6"):
        """
        Consulta a API de forma paginada e 'yields' (gera) os dados de cada página.
        Isso evita carregar todos os dados na memória de uma vez.
        """
        self.logger.info(f"🌐 Iniciando consulta à API para período {start_date} até {end_date}")
        self.logger.info(f"📊 Campanhas: {campaign_ids} | Registros por página: {self.per_page}")
        
        page = 1
        total_pages = 1
        
        while page <= total_pages:
            params = {
                'api_token': self.manager_token,
                'page': page,
                'start_date': start_date,
                'end_date': end_date,
                'include': 'campaign_rel',
                'simple_paginate': 'true',
                'campaign_ids': campaign_ids,
                'per_page': self.per_page
            }
            
            try:
                self.logger.info(f"📥 Consultando página {page}/{total_pages}...")
                
                query_string = '&'.join([f"{key}={quote_plus(str(value))}" for key, value in params.items()])
                full_url = f"{self.base_url}?{query_string}"
                self.logger.debug(f"🔗 URL da requisição: {full_url.replace(self.manager_token, '***')}")

                response = requests.get(full_url, timeout=60)
                response.raise_for_status()
                data = response.json()
                
                if data['status'] != 200:
                    error_msg = f"API retornou status {data['status']}: {data.get('detail', 'Erro desconhecido')}"
                    self.logger.error(f"❌ {error_msg}")
                    break
                
                calls_data = data.get('data', [])
                if not calls_data:
                    if page == 1:
                        self.logger.warning("⚠️ Nenhum dado encontrado na primeira página")
                    else:
                        self.logger.info(f"ℹ️ Página {page} vazia - finalizando consulta")
                    break
                
                self.logger.info(f"✅ Página {page} processada: {len(calls_data)} registros")
                yield calls_data  # Gera os dados da página atual
                
                meta = data.get('meta', {})
                pagination = meta.get('pagination', {})
                total_pages = pagination.get('total_pages', 1)
                
                self.logger.debug(f"📊 Metadados da página: total_pages={total_pages}, current_page={pagination.get('current_page', page)}")
                
                page += 1
                time.sleep(0.5)
                
            except requests.exceptions.Timeout as e:
                self.logger.error(f"⏰ Timeout na requisição da página {page}: {e}")
                break
            except requests.exceptions.RequestException as e:
                self.logger.error(f"🌐 Erro na requisição HTTP da página {page}: {e}")
                break
            except json.JSONDecodeError as e:
                self.logger.error(f"📄 Erro ao decodificar JSON da página {page}: {e}")
                break
            except Exception as e:
                self.logger.error(f"❌ Erro inesperado na página {page}: {e}")
                self.logger.error(f"📝 Traceback: {traceback.format_exc()}")
                break
    
    def save_call_to_db(self, call_data: Dict) -> Tuple[bool, str]:
        """
        Salva um registro de chamada no banco de dados
        Returns: (sucesso: bool, mensagem: str)
        """
        cursor = self.db_manager.get_connection().cursor()
        call_id = call_data.get('id', 'N/A')
        
        try:
            self.logger.debug(f"💾 Salvando chamada ID: {call_id}")
            
            # Dados da rota
            route = call_data.get('route', {})
            
            # Converte call_date para datetime
            call_date = None
            if call_data.get('call_date'):
                try:
                    call_date = datetime.strptime(call_data['call_date'], '%Y-%m-%d %H:%M:%S')
                except ValueError:
                    self.logger.warning(f"⚠️ Formato de data inválido para chamada {call_id}: {call_data.get('call_date')}")
            
            # Insert na tabela calls
            insert_call_sql = """
            INSERT INTO calls (
                id, list_name, number, call_date, call_date_rfc3339, campaign_id, campaign,
                queue_id, queue_name, ring_group_id, ring_group_name, ivr_name, receptive_name, receptive_phone, receptive_did,
                has_agent, agent, acw_time, speaking_time, ivr_time, ivr_after_call_time, amd_time,
                waiting_time, speaking_with_agent_time, route_id, route_name, route_host,
                route_endpoint, route_caller_id, billed_time, billed_value, qualification,
                behavior, readable_behavior_text, phone_type, recording, recording_amd,
                status_id, readable_status_text, readable_amd_status_text, mode,
                hangup_cause, sip_cause, readable_hangup_cause_text, feedback,
                recorded, ended_by_agent, qualification_note, sid, is_dmc,
                is_unknown, is_transferred, is_consult, is_transfer, is_conversion,
                qualification_id, consult_cancelled, recording_transfer, recording_consult,
                recording_after_consult_cancel, ivr_digit_pressed, record_name, transcription, ai_evaluation_status
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """
            
            call_values = (
                call_data.get('id'),
                call_data.get('list'), # Mapeado para list_name
                call_data.get('number'),
                call_date,
                call_data.get('call_date_rfc3339'),
                call_data.get('campaign_id'),
                call_data.get('campaign'),
                call_data.get('queue_id'),
                call_data.get('queue_name'),
                call_data.get('ring_group_id'),
                call_data.get('ring_group_name'),
                call_data.get('ivr_name'),
                call_data.get('receptive_name'),
                call_data.get('receptive_phone'),
                call_data.get('receptive_did'),
                call_data.get('has_agent'),
                call_data.get('agent'),
                call_data.get('acw_time'),
                call_data.get('speaking_time'),
                call_data.get('ivr_time'),
                call_data.get('ivr_after_call_time'),
                call_data.get('amd_time'),
                call_data.get('waiting_time'),
                call_data.get('speaking_with_agent_time'),
                route.get('id') if route else None,
                route.get('name') if route else None,
                route.get('host') if route else None,
                route.get('endpoint') if route else None,
                route.get('caller_id') if route else None,
                call_data.get('billed_time'),
                call_data.get('billed_value'),
                call_data.get('qualification'),
                call_data.get('behavior'),
                call_data.get('readable_behavior_text'),
                call_data.get('phone_type'),
                call_data.get('recording'),
                call_data.get('recording_amd'),
                call_data.get('status_id'),
                call_data.get('readable_status_text'),
                call_data.get('readable_amd_status_text'),
                call_data.get('mode'),
                call_data.get('hangup_cause'),
                call_data.get('sip_cause'),
                call_data.get('readable_hangup_cause_text'),
                call_data.get('feedback'),
                call_data.get('recorded'),
                call_data.get('ended_by_agent'),
                call_data.get('qualification_note'),
                call_data.get('sid'),
                call_data.get('is_dmc'),
                call_data.get('is_unknown'),
                call_data.get('is_transferred'),
                call_data.get('is_consult'),
                call_data.get('is_transfer'),
                call_data.get('is_conversion'),
                call_data.get('qualification_id'),
                call_data.get('consult_cancelled'),
                call_data.get('recording_transfer'),
                call_data.get('recording_consult'),
                call_data.get('recording_after_consult_cancel'),
                call_data.get('ivr_digit_pressed'),
                call_data.get('record_name'),
                call_data.get('transcription'),
                call_data.get('ai_evaluation_status')
            )
            
            cursor.execute(insert_call_sql, call_values)
            
            # Salva dados de mailing se existirem
            mailing_data = call_data.get('mailing_data')
            if mailing_data:
                self.logger.debug(f"📧 Salvando dados de mailing para chamada {call_id}")
                
                insert_mailing_sql = """
                INSERT INTO mailing_data (
                    _id, call_id, identifier, campaign_id, company_id, list_id,
                    uf, phone, dialed_phone, dialed_identifier, on_calling,
                    column_position, row_position, estrategia, razao_social, nome_fantasia,
                    valor_conta, cidade, cep, uf_mailing, socio
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """
                
                data_fields = mailing_data.get('data', {})
                mailing_values = (
                    mailing_data.get('_id'),
                    call_data.get('id'),
                    mailing_data.get('identifier'),
                    mailing_data.get('campaign_id'),
                    mailing_data.get('company_id'),
                    mailing_data.get('list_id'),
                    mailing_data.get('uf'),
                    mailing_data.get('phone'),
                    mailing_data.get('dialed_phone'),
                    mailing_data.get('dialed_identifier'),
                    mailing_data.get('on_calling'),
                    mailing_data.get('column_position'),
                    mailing_data.get('row_position'),
                    data_fields.get('ESTRATEGIA'),
                    data_fields.get('RAZAO SOCIAL'),
                    data_fields.get('NOME FANTASIA'),
                    data_fields.get('VALOR CONTA'),
                    data_fields.get('CIDADE'),
                    data_fields.get('CEP'),
                    data_fields.get('UF'),
                    data_fields.get('SOCIO')
                )
                
                cursor.execute(insert_mailing_sql, mailing_values)
            
            self.db_manager.connection.commit()
            self.logger.debug(f"✅ Chamada {call_id} salva com sucesso")
            return True, f"Chamada {call_id} salva com sucesso"
            
        except pyodbc.IntegrityError as e:
            if "PRIMARY KEY constraint" in str(e):
                msg = f"Registro já existe: {call_id}"
                self.logger.debug(f"ℹ️ {msg}")
                return True, msg  # Considera como sucesso pois o dado já existe
            else:
                msg = f"Erro de integridade ao salvar chamada {call_id}: {e}"
                self.logger.error(f"❌ {msg}")
                return False, msg
        except Exception as e:
            msg = f"Erro inesperado ao salvar chamada {call_id}: {e}"
            self.logger.error(f"❌ {msg}")
            self.logger.error(f"📝 Traceback: {traceback.format_exc()}")
            self.db_manager.connection.rollback()
            return False, msg
        finally:
            cursor.close()
    
    def process_data(self, start_date: str, end_date: str, campaign_ids: str = "5,6") -> Dict[str, int]:
        """
        Processo principal: consulta API e salva no banco
        Returns: dict com estatísticas da execução
        """
        start_time = time.time()
        stats = {
            'total_records': 0,
            'successful_records': 0,
            'failed_records': 0,
            'execution_time': 0
        }
        
        # Registra início da execução
        log_id = self.log_execution_start(start_date, end_date, campaign_ids)
        
        try:
            self.logger.info("🚀 Iniciando processo de coleta e sincronização de dados...")
            self.logger.info(f"📅 Período: {start_date} até {end_date}")
            self.logger.info(f"📊 Campanhas: {campaign_ids}")
            
            # Conecta ao banco
            self.db_manager.get_connection()
            
            # Busca e processa dados da API página por página
            self.logger.info("🌐 Iniciando consulta e salvamento de dados da API...")
            
            total_processed = 0
            for page_data in self.fetch_api_data(start_date, end_date, campaign_ids):
                stats['total_records'] += len(page_data)
                
                if not page_data:
                    continue

                self.logger.info(f"💾 Salvando lote de {len(page_data)} registros...")
                for call_data in page_data:
                    total_processed += 1
                    try:
                        success, message = self.save_call_to_db(call_data)
                        if success:
                            stats['successful_records'] += 1
                        else:
                            stats['failed_records'] += 1
                            self.logger.error(f"❌ Falha no registro {total_processed}: {message}")
                    except Exception as e:
                        stats['failed_records'] += 1
                        self.logger.error(f"❌ Erro crítico ao processar registro {total_processed}: {e}")
                        self.logger.error(f"📝 Traceback: {traceback.format_exc()}")

                self.logger.info(f"📊 Progresso: {stats['successful_records']}/{stats['total_records']} salvos com sucesso.")

            if stats['total_records'] == 0:
                self.logger.warning("⚠️ Nenhum dado retornado pela API para o período.")
                self.log_execution_end(log_id, 0, 0, 0, int(time.time() - start_time), 'COMPLETED_NO_DATA')
                return stats
            
            # Estatísticas finais
            stats['execution_time'] = int(time.time() - start_time)
            
            self.logger.info("="*80)
            self.logger.info("📋 RELATÓRIO FINAL DE EXECUÇÃO")
            self.logger.info("="*80)
            self.logger.info(f"🎯 Total de registros processados: {stats['total_records']}")
            self.logger.info(f"✅ Registros salvos com sucesso: {stats['successful_records']}")
            self.logger.info(f"❌ Registros com falha: {stats['failed_records']}")
            self.logger.info(f"📊 Taxa de sucesso: {(stats['successful_records']/stats['total_records']*100):.1f}%")
            self.logger.info(f"⏱️ Tempo total de execução: {stats['execution_time']} segundos")
            self.logger.info("="*80)
            
            # Registra conclusão da execução
            status = 'COMPLETED_SUCCESS' if stats['failed_records'] == 0 else 'COMPLETED_WITH_ERRORS'
            self.log_execution_end(log_id, stats['total_records'], stats['successful_records'], 
                                 stats['failed_records'], stats['execution_time'], status)
            
        except Exception as e:
            stats['execution_time'] = int(time.time() - start_time)
            error_msg = f"Erro crítico no processo principal: {e}"
            self.logger.error(f"💥 {error_msg}")
            self.logger.error(f"📝 Traceback: {traceback.format_exc()}")
            
            # Registra erro na execução
            self.log_execution_end(log_id, stats['total_records'], stats['successful_records'],
                                 stats['failed_records'], stats['execution_time'], 'FAILED', error_msg)
            
        finally:
            self.db_manager.close_connection()
            
        return stats
    
    def run_daily_sync(self) -> Dict[str, int]:
        """Executa sincronização diária (dia anterior)"""
        yesterday = datetime.now() - timedelta(days=1)
        start_date = yesterday.strftime("%Y-%m-%d 00:00:00")
        end_date = yesterday.strftime("%Y-%m-%d 23:59:59")
        
        self.logger.info("="*80)
        self.logger.info(f"📅 EXECUTANDO SINCRONIZAÇÃO DIÁRIA - {yesterday.strftime('%Y-%m-%d')}")
        self.logger.info("="*80)
        
        return self.process_data(start_date, end_date)
    
    def run_period_sync(self, start_date: str, end_date: str, campaign_ids: str = "5,6") -> Dict[str, int]:
        """Executa sincronização para um período específico"""
        self.logger.info("="*80)
        self.logger.info(f"📅 EXECUTANDO SINCRONIZAÇÃO POR PERÍODO")
        self.logger.info(f"🗓️ De: {start_date}")
        self.logger.info(f"🗓️ Até: {end_date}")
        self.logger.info(f"📊 Campanhas: {campaign_ids}")
        self.logger.info("="*80)
        
        return self.process_data(start_date, end_date, campaign_ids)
    
    def parse_cron_schedule(self, cron_expr: str) -> str:
        """
        Converte expressão CRON em formato do schedule
        Formato CRON: minute hour day_of_month month day_of_week
        """
        self.logger.info(f"📅 Analisando expressão CRON: {cron_expr}")
        
        parts = cron_expr.strip().split()
        if len(parts) != 5:
            self.logger.error(f"❌ Formato CRON inválido: {cron_expr}")
            raise ValueError(f"Formato CRON inválido: {cron_expr}. Use: minute hour day_of_month month day_of_week")
        
        minute, hour, day_month, month, day_week = parts
        
        # Converte para formato legível
        if minute == '0' and hour != '*' and day_month == '*' and month == '*' and day_week == '*':
            # Execução diária em horário específico
            schedule_str = f"daily_at_{hour}:00"
            self.logger.info(f"✅ Agendamento configurado: Diário às {hour}:00")
            return schedule_str
        elif minute != '*' and hour != '*' and day_month == '*' and month == '*' and day_week == '*':
            # Execução diária em horário específico com minutos
            schedule_str = f"daily_at_{hour}:{minute.zfill(2)}"
            self.logger.info(f"✅ Agendamento configurado: Diário às {hour}:{minute.zfill(2)}")
            return schedule_str
        else:
            # Para casos mais complexos, usa configuração padrão
            self.logger.warning(f"⚠️ Expressão CRON complexa detectada: {cron_expr}")
            self.logger.warning("🔄 Usando configuração padrão: Diário às 02:00")
            return "daily_at_2:00"
    
    def schedule_job(self):
        """Configura e executa o agendamento baseado no CRON"""
        self.logger.info("⏰ Configurando agendamento de execução...")
        
        try:
            schedule_format = self.parse_cron_schedule(self.cron_schedule)
            
            if schedule_format.startswith("daily_at_"):
                time_part = schedule_format.replace("daily_at_", "")
                schedule.every().day.at(time_part).do(self.run_daily_sync)
                self.logger.info(f"✅ Job agendado para execução diária às {time_part}")
            
        except Exception as e:
            self.logger.error(f"❌ Erro ao configurar agendamento: {e}")
            self.logger.info("🔄 Usando configuração padrão: Diário às 02:00")
            schedule.every().day.at("02:00").do(self.run_daily_sync)
    
    def run_scheduler(self):
        """Executa o loop principal do agendador"""
        self.logger.info("🤖 Iniciando robô em modo agendado...")
        self.logger.info(f"📅 Configuração CRON: {self.cron_schedule}")
        
        # Configura agendamento
        self.schedule_job()
        
        self.logger.info("⏳ Aguardando horário de execução...")
        self.logger.info("💡 Para parar o robô, use Ctrl+C")
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Verifica a cada minuto
                
        except KeyboardInterrupt:
            self.logger.info("🛑 Robô interrompido pelo usuário")
        except Exception as e:
            self.logger.error(f"❌ Erro no loop principal: {e}")
            self.logger.error(f"📝 Traceback: {traceback.format_exc()}")
    
    def run_manual_execution(self):
        """Executa uma única vez (modo manual)"""
        self.logger.info("🔧 Executando robô em modo manual...")
        
        # Verifica se há parâmetros específicos nas variáveis de ambiente
        start_date = os.getenv('MANUAL_START_DATE')
        end_date = os.getenv('MANUAL_END_DATE')
        campaign_ids = os.getenv('MANUAL_CAMPAIGN_IDS', '5,6')
        
        if start_date and end_date:
            self.logger.info(f"📅 Parâmetros manuais detectados:")
            self.logger.info(f"   🗓️ Data início: {start_date}")
            self.logger.info(f"   🗓️ Data fim: {end_date}")
            self.logger.info(f"   📊 Campanhas: {campaign_ids}")
            return self.run_period_sync(start_date, end_date, campaign_ids)
        else:
            self.logger.info("📅 Executando sincronização do dia anterior...")
            return self.run_daily_sync()


def main():
    """Função principal"""
    try:
        robot = API3CRobot()
        
        # Verifica modo de execução
        execution_mode = os.getenv('EXECUTION_MODE', 'scheduled').lower()
        
        robot.logger.info(f"🎯 Modo de execução: {execution_mode.upper()}")
        
        if execution_mode == 'manual':
            # Execução única
            stats = robot.run_manual_execution()
            robot.logger.info("✅ Execução manual concluída")
            
        elif execution_mode == 'scheduled':
            # Execução agendada
            robot.run_scheduler()
            
        else:
            robot.logger.error(f"❌ Modo de execução inválido: {execution_mode}")
            robot.logger.info("💡 Modos válidos: 'manual' ou 'scheduled'")
            sys.exit(1)
        
    except KeyboardInterrupt:
        print("\n🛑 Execução interrompida pelo usuário")
        sys.exit(0)
    except Exception as e:
        print(f"💥 Erro crítico na execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
    input("Pressione Enter para sair...")