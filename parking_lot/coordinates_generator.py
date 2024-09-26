import cv2 as open_cv
import numpy as np
from colors import COLOR_WHITE
from drawing_utils import draw_contours
import yaml

class CoordinatesGenerator:
    KEY_RESET = ord("r")
    KEY_QUIT = ord("q")
    KEY_DONE = ord("d")

    def _init_(self, image, output_file, color):
        self.output_file = output_file
        self.caption = "Selecione as vagas"
        self.color = color

        self.image = open_cv.imread(image)
        self.original_image = self.image.copy()
        self.click_count = 0
        self.ids = 0
        self.coordinates = []
        self.parking_data = []

        open_cv.namedWindow(self.caption, open_cv.WINDOW_GUI_EXPANDED)
        open_cv.setMouseCallback(self.caption, self.__mouse_callback)

    def generate(self):
        print("Selecione as vagas clicando nos quatro cantos de cada vaga.")
        print("Pressione 'r' para resetar a seleção, 'd' para finalizar ou 'q' para sair sem salvar.")
        
        while True:
            open_cv.imshow(self.caption, self.image)
            key = open_cv.waitKey(1) & 0xFF

            if key == CoordinatesGenerator.KEY_RESET:
                self.image = self.original_image.copy()
                self.coordinates = []
                self.click_count = 0
                self.parking_data = []
                print("Seleção resetada. Recomece a seleção das vagas.")
            elif key == CoordinatesGenerator.KEY_DONE:
                if len(self.parking_data) == 0:
                    print("Nenhuma vaga foi selecionada. Selecione as vagas antes de finalizar.")
                else:
                    with open(self.output_file, 'w') as f:
                        yaml.dump(self.parking_data, f)
                    print(f"Coordenadas salvas em {self.output_file}")
                    break
            elif key == CoordinatesGenerator.KEY_QUIT:
                print("Saindo sem salvar.")
                break

        open_cv.destroyWindow(self.caption)

    def __mouse_callback(self, event, x, y, flags, params):
        if event == open_cv.EVENT_LBUTTONDOWN:
            self.coordinates.append((x, y))
            self.click_count += 1

            if self.click_count >= 2:
                self.__handle_click_progress()

            if self.click_count == 4:
                self.__handle_done()
                self.click_count = 0
                self.coordinates = []

        open_cv.imshow(self.caption, self.image)

    def __handle_click_progress(self):
        open_cv.line(self.image, self.coordinates[-2], self.coordinates[-1], (255, 0, 0), 1)

    def __handle_done(self):
        open_cv.line(self.image, self.coordinates[-1], self.coordinates[0], (255, 0, 0), 1)

        coordinates = np.array(self.coordinates)

        parking_spot = {
            'id': self.ids,
            'coordinates': [list(coord) for coord in self.coordinates]
        }
        self.parking_data.append(parking_spot)

        draw_contours(self.image, coordinates, str(self.ids + 1), COLOR_WHITE)

        self.ids += 1