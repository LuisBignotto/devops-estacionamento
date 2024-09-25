import cv2 as open_cv
import numpy as np
from colors import COLOR_WHITE
from drawing_utils import draw_contours


class CoordinatesGenerator:
    KEY_RESET = ord("r")
    KEY_QUIT = ord("q")

    def __init__(self, image_path, output, color):
        self.output = output
        self.caption = image_path
        self.color = color

        self.image = open_cv.imread(image_path).copy()
        self.click_count = 0
        self.ids = 0
        self.coordinates = []

        open_cv.namedWindow(self.caption, open_cv.WINDOW_GUI_EXPANDED)
        open_cv.setMouseCallback(self.caption, self.__mouse_callback)

    def generate(self):
        while True:
            open_cv.imshow(self.caption, self.image)
            key = open_cv.waitKey(0)

            if key == CoordinatesGenerator.KEY_RESET:
                self.image = open_cv.imread(self.caption).copy()  # Reiniciar para a imagem original
            elif key == CoordinatesGenerator.KEY_QUIT:
                break

        open_cv.destroyWindow(self.caption)

    def __mouse_callback(self, event, x, y, flags, params):
        if event == open_cv.EVENT_LBUTTONDOWN:
            self.coordinates.append((x, y))
            self.click_count += 1

            if self.click_count >= 4:
                self.__handle_done()
            elif self.click_count > 1:
                self.__handle_click_progress()

        open_cv.imshow(self.caption, self.image)

    def __handle_click_progress(self):
        # Desenhar uma linha entre os dois últimos pontos
        open_cv.line(self.image, self.coordinates[-2], self.coordinates[-1], (255, 0, 0), 1)

    def __handle_done(self):
        # Desenhar o retângulo final usando os últimos quatro pontos
        open_cv.line(self.image, self.coordinates[2], self.coordinates[3], self.color, 1)
        open_cv.line(self.image, self.coordinates[3], self.coordinates[0], self.color, 1)

        # Reiniciar a contagem de cliques e preparar para o próximo conjunto de coordenadas
        self.click_count = 0
        self.__save_coordinates()

        # Limpar as coordenadas para o próximo retângulo
        self.coordinates.clear()
        self.ids += 1

    def __save_coordinates(self):
        # Formatar as coordenadas para saída
        coordinates_str = ', '.join(f"[{x}, {y}]" for x, y in self.coordinates)
        output_line = f"-\n          id: {self.ids}\n          coordinates: [{coordinates_str}]\n"
        self.output.write(output_line)

        # Desenhar o contorno na imagem
        draw_contours(self.image, np.array(self.coordinates), str(self.ids + 1), COLOR_WHITE)
