import cv2
import imutils
import numpy as np
import cairosvg

class TemplateDetector:
    def __init__(self, template_filename, tattoo_svg_filename):
        template1 = cv2.imread(template_filename)
        template1 = cv2.cvtColor(template1, cv2.COLOR_BGR2GRAY)

        template1 = cv2.Canny(template1, 80, 95)
        self.template = imutils.resize(template1, width=60)
        (self.tH, self.tW) = self.template.shape[:2]

        self.tattoo_svg_filename = tattoo_svg_filename

        # Store the original tattoo SVG content
        with open(self.tattoo_svg_filename, "rb") as svg_file:
            self.tattoo_svg_content = svg_file.read()

        self.tattoo_png = None  # Store the PNG version of the tattoo


        self.found = None
        self.x_offset = 0
        self.y_offset = 0

    def resize_svg(self, scale):
        # Convert SVG to a rasterized PNG at a specific scale
        png_image = cairosvg.svg2png(bytestring=self.tattoo_svg_content, scale=scale)
        nparr = np.frombuffer(png_image, np.uint8)
        png_raster = cv2.imdecode(nparr, cv2.IMREAD_UNCHANGED)
        return png_raster

    def detect_template(self, frame):
        # Convert frame to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        self.found = (0, None, 0)  # Initialize self.found with default values

        # Loop over the scales of the image
        for scale in np.linspace(0.2, 1.0, 20)[::-1]:
            # Resize the image according to the scale
            resized = cv2.resize(gray, None, fx=scale, fy=scale, interpolation=cv2.INTER_AREA)
            r = gray.shape[1] / float(resized.shape[1])

            if resized.shape[0] < self.tH or resized.shape[1] < self.tW:
                print("frame is smaller than the template")
                break

            # Detect edges in the resized grayscale image
            edged = cv2.Canny(resized, 75, 95)
            # Template match to find the template in the image
            result = cv2.matchTemplate(edged, self.template, cv2.TM_CCOEFF)
            (minVal, maxVal, _, maxLoc) = cv2.minMaxLoc(result)

            # Update if found greater correlation value
            if self.found[1] is None or maxVal > self.found[0]:
                self.found = (maxVal, maxLoc, r)

        if self.found[0] >= 12e5:
            self.tattoo_png = self.resize_svg(self.found[2])  # Resize the SVG to match the template scale
            self.tattoo_png = self.tattoo_png.tobytes()  # Convert to bytes for CV2 processing
            print("Template detected")  # Print when template is successfully detected

    def draw_tattoo(self, frame):
        if self.found[0] >= 12e5 and self.tattoo_png is not None:
            h, w = self.template.shape

            # Convert the tattoo PNG bytes to a numpy array
            tattoo_array = np.frombuffer(self.tattoo_png, dtype=np.uint8)
            tattoo_img = cv2.imdecode(tattoo_array, cv2.IMREAD_UNCHANGED)

            y_offset, x_offset = self.found[1]  # Get the location of the template

            # Ensure the tattoo image fits within the frame boundaries
            if y_offset + tattoo_img.shape[0] <= frame.shape[0] and x_offset + tattoo_img.shape[1] <= frame.shape[1]:
                # Overlay the tattoo image on the frame
                for c in range(0, 3):
                    frame[y_offset:y_offset + tattoo_img.shape[0], x_offset:x_offset + tattoo_img.shape[1], c] = (
                        tattoo_img[..., c] * (tattoo_img[..., 3] / 255.0) +
                        frame[y_offset:y_offset + tattoo_img.shape[0], x_offset:x_offset + tattoo_img.shape[1], c] *
                        (1.0 - tattoo_img[..., 3] / 255.0)
                    )

        return frame
