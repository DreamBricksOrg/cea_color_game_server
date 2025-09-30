import structlog
from flask import Flask, render_template, send_file
import logging
import sys
from image_controller import ImageController
from log_sender import save_csv
import threading
import parameters as pm
from qrcodeaux import generate_qr_code

structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

# Configuração do logging padrão
logging.basicConfig(
    format="%(message)s",
    stream=sys.stdout,
    level=logging.INFO,
)

# Criação da aplicação Flask
app = Flask(__name__)

# Logger estruturado
logger = structlog.get_logger()

image_controller = ImageController()

# init_csv(csv_filename)
# init_csv(backup_filename)

# threading.Thread(target=process_csv_and_send_logs, args=(csv_filename, backup_filename), daemon=True).start()

@app.route('/')
def hello_world():
    """Rota principal que renderiza a página Hello World"""
    logger.info("Página Hello World acessada", route="/", method="GET")
    return render_template('index.html')

@app.route('/qr')
def get_qrcode_score():
    image_id = image_controller.get_most_recent_file()
    qr_image = generate_qr_code(
        pm.BASE_URL + '/download_image_page/' + image_id)
    return send_file(qr_image, mimetype='image/png')

@app.route('/download_image/<filename>')
def download_image(filename):
    if image_controller.check_image_exists(filename):
        return send_file(image_controller.get_image_path(filename), mimetype='image/png')
    else:
        return render_template('error.html', message="File not found"), 404
        
@app.route('/download_image_page/<filename>')
def download_image_page(filename):
    if image_controller.check_image_exists(filename):
        # save_csv("ACESSOU_QR_CODE")
        image_url = f"/download_image/{filename}"
        return render_template('download.html', image_url=image_url)
    else:
        return render_template('error.html', message="File not found"), 404


@app.errorhandler(404)
def not_found(error):
    """Handler para páginas não encontradas"""
    logger.warning("Página não encontrada", error=str(error), status_code=404)
    return "<h1>Página não encontrada</h1>", 404

@app.errorhandler(500)
def internal_error(error):
    """Handler para erros internos do servidor"""
    logger.error("Erro interno do servidor", error=str(error), status_code=500)
    return "<h1>Erro interno do servidor</h1>", 500

if __name__ == '__main__':
    logger.info("Iniciando aplicação Flask", port=5000, debug=True)
    app.run(debug=True, host='0.0.0.0', port=5000)