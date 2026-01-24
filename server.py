from waitress import serve
from app import app # Importa o seu app Flask

# Configuração
HOST = '0.0.0.0' # Permite acesso de outros PCs
PORT = 8080      # Porta de acesso (pode ser 80, 5000, 8080)

print(f"--- PrintFlow Iniciado ---")
print(f"Acesse no navegador através do IP deste computador na porta {PORT}")
print(f"Exemplo: http://192.168.X.X:{PORT}")
print("Pressione Ctrl+C para parar o servidor.")

serve(app, host=HOST, port=PORT, threads=6, max_request_body_size=500*1024*1024)