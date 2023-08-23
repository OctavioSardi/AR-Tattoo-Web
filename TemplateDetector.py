import cv2
import imutils
import numpy as np

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
        if self.found[0] < 12e5:
            # Correlation too low
            pass
        else:
            # Show bounding box and tattoo
            (_, maxLoc, r) = self.found
            (startX, startY) = (int(maxLoc[0] * r), int(maxLoc[1] * r))
            (endX, endY) = (int((maxLoc[0] + self.tW) * r), int((maxLoc[1] + self.tH) * r))

            # Remove template
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            edged = cv2.Canny(gray, 80, 100)
            sub_canny = edged[startY:endY, startX:endX]
            sub_frame = frame[startY:endY, startX:endX]
            # Dilate canny edges
            kernel = np.ones((3, 3), np.uint8)
            dilate = cv2.dilate(sub_canny, kernel, iterations=5)
            dilate = cv2.bitwise_not(dilate)
            # Remove template from sub-frame
            sub_frame = cv2.bitwise_or(sub_frame, sub_frame, mask=dilate)
            # Inpaint sub-frame
            dilate = cv2.bitwise_not(dilate)
            inpaint = cv2.inpaint(sub_frame, dilate, 3, cv2.INPAINT_TELEA)

            frame[startY:endY, startX:endX] = inpaint

            # Draw the stored PNG tattoo image over the template region
            if self.tattoo_png is not None:
                y1 = startY + self.y_offset
                y1 = 0 if y1 < 0 else y1
                y2 = y1 + self.tattoo_png.shape[0]

                x1 = startX + self.x_offset
                x1 = 0 if x1 < 0 else x1
                x2 = x1 + self.tattoo_png.shape[1]

                if y2 < frame.shape[0] and x2 < frame.shape[1]:
                    # Tattoo fits frame
                    for c in range(0, 3):
                        # Apply tattoo with transparency to image
                        alpha = self.tattoo_png[:, :, 2] / 255.0
                        color = self.tattoo_png[:, :, c] * (1.0 - alpha)
                        beta = frame[y1:y2, x1:x2, c] * alpha
                        frame[y1:y2, x1:x2, c] = color + beta

        return frame
