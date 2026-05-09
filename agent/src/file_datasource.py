from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
from domain.parking import Parking
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
        parking_filename: str,
    ) -> None:
        self._accelerometer_filename = accelerometer_filename
        self._gps_filename = gps_filename
        self._parking_filename = parking_filename
        self._parking_file = None

    def _read_next_parking(self) -> Parking:
        row = next(self._parking_reader, None)
        if row is None:
            self._parking_file.seek(0)
            self._parking_reader = reader(self._parking_file)
            next(self._parking_reader)  # skip header
            row = next(self._parking_reader)

        empty_count = int(row[0])
        longitude = float(row[1])
        latitude = float(row[2])
        return Parking(empty_count, Gps(longitude, latitude))

    def read(self) -> AggregatedData:
        """Метод повертає дані отримані з датчиків"""
        parking = self._read_next_parking()
        return AggregatedData(
            Accelerometer(1, 2, 3),
            Gps(4, 5),
            datetime.now(),
            config.USER_ID,
            parking,
        )

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""
        if self._parking_file is not None:
            self._parking_file.close()
        self._parking_file = open(
            self._parking_filename, newline="", encoding="utf-8"
        )
        self._parking_reader = reader(self._parking_file)
        next(self._parking_reader)  # skip header

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
        if self._parking_file is not None:
            self._parking_file.close()
            self._parking_file = None
