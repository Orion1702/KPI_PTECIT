from csv import reader
from datetime import datetime
from domain.accelerometer import Accelerometer
from domain.gps import Gps
from domain.aggregated_data import AggregatedData
import config


class FileDatasource:
    def __init__(
        self,
        accelerometer_filename: str,
        gps_filename: str,
    ) -> None:
        pass

    def read(self) -> AggregatedData:
        # Приклад зчитування одного рядка
		row_acc = next(self.acc_reader) # [cite: 224, 241]
		row_gps = next(self.gps_reader)
        """Метод повертає дані отримані з датчиків"""
        return AggregatedData(
            # Accelerometer(1, 2, 3),
            # Gps(4, 5),
            # datetime.now(),
            # config.USER_ID,
            Accelerometer(int(row_acc[0]), int(row_acc[1]), int(row_acc[2])), # Обов'язково int()! [cite: 101, 102, 103]
			Gps(float(row_gps[0]), float(row_gps[1])), # Обов'язково float()! [cite: 115, 117]
			datetime.now() # [cite: 141]
        )
    
	# def read(self) -> AggregatedData:
	# 	# Приклад зчитування одного рядка
	# 	row_acc = next(self.acc_reader) # [cite: 224, 241]
	# 	row_gps = next(self.gps_reader)

	# 	return AggregatedData(
	# 		Accelerometer(int(row_acc[0]), int(row_acc[1]), int(row_acc[2])), # Обов'язково int()! [cite: 101, 102, 103]
	# 		Gps(float(row_gps[0]), float(row_gps[1])), # Обов'язково float()! [cite: 115, 117]
	# 		datetime.now() # [cite: 141]
	# 	)

    def startReading(self, *args, **kwargs):
        """Метод повинен викликатись перед початком читання даних"""

    def stopReading(self, *args, **kwargs):
        """Метод повинен викликатись для закінчення читання даних"""
