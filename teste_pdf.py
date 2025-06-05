import pdfkit
import subprocess

# Teste wkhtmltopdf
try:
    result = subprocess.run(['wkhtmltopdf', '--version'], capture_output=True, text=True)
    print(f"✅ wkhtmltopdf: {result.stdout.strip()}")
except:
    print("❌ wkhtmltopdf não encontrado")

# Teste pdfkit
try:
    html = "<h1>Teste Codespace</h1><p>PDF funcionando!</p>"
    pdf = pdfkit.from_string(html, False)
    print(f"✅ PDF gerado! Tamanho: {len(pdf)} bytes")
except Exception as e:
    print(f"❌ Erro: {e}")
