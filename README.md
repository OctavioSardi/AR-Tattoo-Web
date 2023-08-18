# Web Frontend for AR Tattoo

The purpose of this app is to experiment on how to use artificial vision technologies, such as Augmented Reality, on the browser.

## Technologies Used

- Python 3
- Flask
- Numpy
- OpenCV
- HTML

Install Flask, Numpy and OpenCV through pip to use the program.

## Functionallity

1. Draw over a piece of paper or any distinguishable surface (like your skin) the same pattern that is in the ```template.png``` file.
2. Launch the app: ```python web.py```
3. The app will now scan real time images with the webcam and try to find the matching template. When it does, it will replace it with the ```tattoo.png``` image under the **img** directory.
4. If you want to change the tattoo design, take the following into consideration:
	1. It must be a **png** immage
	2. It must have some form of solid background (prefereably white)
	3. Image quality will degrade, so the higher the resolution the better

## Acknowledgments

- [tiagoyukio12](https://github.com/tiagoyukio12/tattoo-AR), for the code that would serve as the building block for this proyect
- [Aprende e Ingenia](https://www.youtube.com/watch?v=ZWj6_RRlP_U), for showing how to connect the backend to a web frontend
