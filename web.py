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

    # while True:
    while video_capture.isOpened():
        ret, frame = cap.read()

        if not ret:
            break

        else:
            frameRGB = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Detect the template in the frame
            template_detector.detect_template(frame)

            # Draw the tattoo if template is found
            if template_detector.found[0] > 12e5:
                scale = template_detector.found[2]
                resized_tattoo = template_detector.resize_svg(scale)
                modified_frame = template_detector.draw_tattoo(frame.copy())
                cv2.imshow('Modified Frame', modified_frame)

            suc, encode = cv2.imencode('.jpg', frame)
            frame = encode.tobytes()

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

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
