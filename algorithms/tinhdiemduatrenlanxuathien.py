# Date: 09/05/2025
# Auth: Luvideez
# ID: 000002
from algorithms.base import BaseAlgorithm
import datetime
import logging
from collections import defaultdict
import math
logger = logging.getLogger(__name__)

class Tinh_diem_dua_tren_do_moi(BaseAlgorithm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {'description': 'Tính điểm dựa trên độ mới (lần cuối xuất hiện)', 'parameters': {'multiplier_algo1': 1.0, 'freqBonus': 1.05, 'freqMaxBonus': 8.5, 'cycleBonusFactor': 0.9, 'prizeSpecialBonus': 10.0, 'prizeLowBonus': 5.0, 'multiplier_algo2': 1.0, 'hotBonus': 1.0, 'hotMaxBonus': 5.0, 'multiplier_algo3': 1.0, 'multiplier_algo4': 1.0, 'lookbackDays': 14, 'multiplier_algo6': 1.0, 'frequencyMultiplier': 1.0}}
        self._log('debug', f'{self.__class__.__name__} initialized.')

    def predict(self, date_to_predict: datetime.date, historical_results: list) -> dict:
        self._log('debug', f'Predicting for {date_to_predict}')
        scores = {f'{i:02d}': 0.0 for i in range(100)}
        if not historical_results:
            self._log('warning', 'Not enough historical data.')
            return scores
        number_data = defaultdict(lambda: {'last_appearance': None, 'appearances': [], 'avgCycle': 0, 'recentFrequency': 0})
        for result in historical_results:
            date = result['date']
            numbers = self.extract_numbers_from_dict(result['result'])
            for num in numbers:
                number_data[num]['appearances'].append(date)
        for num, data in number_data.items():
            if data['appearances']:
                data['last_appearance'] = max(data['appearances'])
                data['avgCycle'] = (date_to_predict - min(data['appearances'])).days / len(data['appearances']) if len(data['appearances']) > 1 else 0
                data['recentFrequency'] = sum((1 for date in data['appearances'] if (date_to_predict - date).days <= 30))
        for i in range(100):
            num_str = f'{i:02d}'
            num = i
            if num in number_data and number_data[num]['appearances']:
                last_appearance = number_data[num]['last_appearance']
                daysDiff = (date_to_predict - last_appearance).days
                adjustedWeight = 1.0 if daysDiff <= 7 else 0.5 if daysDiff <= 15 else 0.2
                frequencyBonus = min(self.config['parameters']['freqBonus'] * number_data[num]['recentFrequency'], self.config['parameters']['freqMaxBonus'])
                cycleBonus = self.config['parameters']['cycleBonusFactor'] * math.exp(-abs(daysDiff - number_data[num]['avgCycle'])) if number_data[num]['avgCycle'] > 0 else 0
                prizeBonus = self.config['parameters']['prizeSpecialBonus'] if any((num in self.extract_numbers_from_dict(result['result']) and 'special' in result['result'] for result in historical_results if (date_to_predict - result['date']).days <= 30)) else self.config['parameters']['prizeLowBonus'] if any((num in self.extract_numbers_from_dict(result['result']) for result in historical_results if (date_to_predict - result['date']).days <= 30)) else 0
                scores[num_str] += (adjustedWeight * daysDiff + frequencyBonus + cycleBonus + prizeBonus) * self.config['parameters']['multiplier_algo1']
        self._log('info', f'Prediction finished for {date_to_predict}. Generated {len(scores)} scores.')
        return scores