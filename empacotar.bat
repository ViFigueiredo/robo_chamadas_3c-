@echo off
REM === Empacotamento do robo_neo ===

REM 0. Limpar a pasta dist se já existir
if exist dist (
    rmdir /S /Q dist
)

REM 1. Gerar o executável com PyInstaller
pyinstaller --clean --onefile --name robo_disc_3cmais app.py

REM 2. Copiar arquivos de configuração e drivers para a pasta dist
copy /Y .env dist\

REM 3. Mensagem final
cd dist
@echo =====================================
@echo Empacotamento concluído!
@echo Para rodar em produção, use apenas os arquivos desta pasta.
@echo =====================================
pause 