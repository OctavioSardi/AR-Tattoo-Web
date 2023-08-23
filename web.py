# Importamos librerias
from flask import Flask, render_template, Response
import cv2
from TemplateDetector import TemplateDetector

# Realizamos la Videocaptura
cap = cv2.VideoCapture(0)

# Creamos la app
app =  Flask(__name__)

# Inicializamos el TemplateDetector con los paths al patron y al tatuaje
template_detector = TemplateDetector('Template.png', 'Tattoo.svg')


# Mostramos el video en RT

def gen_frame():

    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = int(cap.get(cv2.CAP_PROP_FPS))

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, width)  # Set width to 1280 pixels
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height)  # Set height to 720 pixels
    cap.set(cv2.CAP_PROP_FPS, fps)  # Set framerate to 240fps

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        # Detect the template
        template_detector.detect_template(frame)

        # Draw the tattoo if template is detected
        frame_with_tattoo = template_detector.draw_tattoo(frame)

        # Convert the modified frame to JPEG format
        _, buffer = cv2.imencode('.jpg', frame_with_tattoo)
        frame_with_tattoo_bytes = buffer.tobytes()

        yield (b'--frame\r\n'
                b'Content-Type: image/jpeg\r\n\r\n' + frame_with_tattoo_bytes + b'\r\n')

    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ruta de aplicacion 'principal'
@app.route('/')
def index():
    return render_template('index.html')

# Ruta del video
@app.route('/video')
def video():
    return Response(gen_frame(), mimetype='multipart/x-mixed-replace; boundary=frame')

# Ejecutamos la app
if __name__ == "__main__":
    app.run(debug = True)
