import cv2
import numpy as np

class ParkingDetector:
    def __init__(self):
        self.statuses = {}
        self.running = False
        self.coordinates_data = []
        self.reference_frame = None
        self.contours = []
        self.bounds = []
        self.mask = []

    def start_detection(self):
        self.running = True

    def stop_detection(self):
        self.running = False

    def update_coordinates(self, coordinates):
        self.coordinates_data = []
        for idx, coord in enumerate(coordinates):
            self.coordinates_data.append({
                'id': str(idx + 1),
                'coordinates': [{'x': point['x'], 'y': point['y']} for point in coord]
            })
        self.initialize_parking_spaces()
        self.reference_frame = None

    def initialize_parking_spaces(self):
        self.contours = []
        self.bounds = []
        self.mask = []
        self.statuses = {}
        for p in self.coordinates_data:
            coordinates = np.array([[point['x'], point['y']] for point in p['coordinates']], dtype=int)
            rect = cv2.boundingRect(coordinates)
            new_coordinates = coordinates.copy()
            new_coordinates[:, 0] -= rect[0]
            new_coordinates[:, 1] -= rect[1]

            self.contours.append(coordinates)
            self.bounds.append(rect)

            mask = cv2.drawContours(
                np.zeros((rect[3], rect[2]), dtype=np.uint8),
                [new_coordinates],
                contourIdx=-1,
                color=255,
                thickness=-1,
                lineType=cv2.LINE_8)
            mask = mask == 255
            self.mask.append(mask)
            self.statuses[p['id']] = False

    def detect_motion(self, frame):
        grayed = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if self.reference_frame is None:
            self.reference_frame = grayed
            return frame

        for index, p in enumerate(self.coordinates_data):
            status = self.__apply(grayed, index, p)
            self.statuses[p['id']] = status
            coordinates = self.contours[index]
            color = (0, 0, 255) if status else (0, 255, 0)
            cv2.drawContours(frame, [coordinates], contourIdx=-1, color=color, thickness=2)

        return frame

    def __apply(self, grayed, index, p):
        rect = self.bounds[index]
        roi_current = grayed[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]
        roi_reference = self.reference_frame[rect[1]:rect[1] + rect[3], rect[0]:rect[0] + rect[2]]

        diff = cv2.absdiff(roi_current, roi_reference)
        _, diff = cv2.threshold(diff, 30, 255, cv2.THRESH_BINARY)

        diff = cv2.bitwise_and(diff, diff, mask=self.mask[index].astype(np.uint8))

        white_pixels = np.sum(diff == 255)
        total_pixels = np.sum(self.mask[index])
        occupancy_ratio = white_pixels / total_pixels if total_pixels > 0 else 0

        status = occupancy_ratio > 0.15
        return status
