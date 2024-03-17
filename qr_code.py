from flask import Flask, render_template_string
import qrcode
import io
import base64
import random

app = Flask(__name__)

def generate_qr_data():
    lecture_data = "Lecture ID: 8\nDate: 2024-03-14\nRandom Number: " + str(random.randint(1000, 9999))
    
    return lecture_data

@app.route('/')
def index():
    lecture_data = generate_qr_data()

    # Generate QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(lecture_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 string
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return render_template_string(
        """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="utf-8">
            <title>QR Code for Lecture</title>
            

        </head>
        <body>
            <div class="modal fade" id="qrCodeModal" tabindex="-1" aria-labelledby="qrCodeModalLabel" aria-hidden="true">
                <div class="modal-dialog modal-dialog-centered modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title" id="qrCodeModalLabel">QR Code for Lecture</h5>
                        </div>
                        <div class="modal-body text-center">
                            <img id="qrCodeImg" src="data:image/png;base64,{{ qr_code }}" alt="QR Code">
                        </div>
                    </div>
                </div>
            </div>
        <script>
            function refreshQRCode() {
                location.reload();
            }
            setInterval(refreshQRCode, 10000); // Refresh every 10 seconds
            </script>
        </body>
        </html>
        """,
        qr_code=img_str
    )

@app.route('/qr_code')
def qr_code():
    lecture_data = generate_qr_data()

    # Generate QR code
    qr = qrcode.QRCode(version=1, error_correction=qrcode.constants.ERROR_CORRECT_L, box_size=10, border=4)
    qr.add_data(lecture_data)
    qr.make(fit=True)

    # Create image
    img = qr.make_image(fill_color="black", back_color="white")

    # Convert image to base64 string
    buffered = io.BytesIO()
    img.save(buffered)
    img_str = base64.b64encode(buffered.getvalue()).decode("utf-8")

    return img_str

if __name__ == '__main__':
    app.run(debug=True)
