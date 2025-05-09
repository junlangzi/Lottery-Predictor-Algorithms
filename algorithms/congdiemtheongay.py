# Date: 09/05/2025
# Auth: Luvideez
# ID: 000002
from algorithms.base import BaseAlgorithm
import datetime

class CongdiemtheongayAlgorithm(BaseAlgorithm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.config = {'description': 'Cộng điểm dựa trên số ngày chưa xuất hiện của một con số, có tính đến điểm thưởng Fibonacci và bonus theo nhóm ngày.', 'parameters': {'today_hit_penalty': -10.0, 'score_day_1_2': 1.0, 'score_day_3': 2.0, 'score_day_4': 3.0, 'score_day_5': 5.0, 'score_day_6': 8.0, 'fibo_start_day': 7, 'fibo_initial_a': 1.0, 'fibo_initial_b': 1.0, 'bonus_divisor': 6, 'bonus_value_per_group': 1.0}}
        self._log('debug', f'{self.__class__.__name__} initialized.')

    def predict(self, date_to_predict: datetime.date, historical_results: list) -> dict:
        self._log('debug', f'Predicting for {date_to_predict}')
        scores = {f'{i:02d}': 0.0 for i in range(100)}
        if not historical_results:
            self._log('warning', 'No historical results provided.')
            return scores
        params = self.config.get('parameters', {})
        try:
            today_penalty = float(params.get('today_hit_penalty', -10.0))
            s_d_1_2 = float(params.get('score_day_1_2', 1.0))
            s_d_3 = float(params.get('score_day_3', 2.0))
            s_d_4 = float(params.get('score_day_4', 3.0))
            s_d_5 = float(params.get('score_day_5', 5.0))
            s_d_6 = float(params.get('score_day_6', 8.0))
            f_start_day = int(params.get('fibo_start_day', 7))
            f_init_a = float(params.get('fibo_initial_a', 1.0))
            f_init_b = float(params.get('fibo_initial_b', 1.0))
            b_divisor = int(params.get('bonus_divisor', 5))
            b_val_group = float(params.get('bonus_value_per_group', 1.0))
            if b_divisor <= 0:
                self._log('warning', f'bonus_divisor is {b_divisor}, which is invalid. Defaulting to 5.')
                b_divisor = 5
            if f_start_day <= 0:
                self._log('warning', f'fibo_start_day is {f_start_day}, which is invalid. Defaulting to 7.')
                f_start_day = 7
        except (ValueError, TypeError) as e:
            self._log('error', f'Invalid parameters in config for {self.__class__.__name__}: {e}. Using defaults for all.')
            today_penalty = -10.0
            s_d_1_2 = 1.0
            s_d_3 = 2.0
            s_d_4 = 3.0
            s_d_5 = 5.0
            s_d_6 = 8.0
            f_start_day = 7
            f_init_a = 1.0
            f_init_b = 1.0
            b_divisor = 5
            b_val_group = 1.0
        most_recent_historical_date = None
        if historical_results:
            valid_historical_dates = [res['date'] for res in historical_results if res['date'] < date_to_predict]
            if valid_historical_dates:
                most_recent_historical_date = max(valid_historical_dates)
        last_occurrence = {}
        sorted_history = sorted(historical_results, key=lambda x: x['date'])
        for result_entry in sorted_history:
            if result_entry['date'] < date_to_predict:
                numbers_in_day = self.extract_numbers_from_dict(result_entry.get('result', {}))
                for num in numbers_in_day:
                    last_occurrence[num] = result_entry['date']
        today_numbers_set = set()
        if most_recent_historical_date:
            for result_entry in sorted_history:
                if result_entry['date'] == most_recent_historical_date:
                    today_numbers_set.update(self.extract_numbers_from_dict(result_entry.get('result', {})))
                    break
        for num_val in range(100):
            num_str_format = f'{num_val:02d}'
            points = 0.0
            if num_val in today_numbers_set:
                points = today_penalty
            elif num_val in last_occurrence:
                days_since_last = (date_to_predict - last_occurrence[num_val]).days
                if 1 <= days_since_last <= 2:
                    points = s_d_1_2
                elif days_since_last == 3:
                    points = s_d_3
                elif days_since_last == 4:
                    points = s_d_4
                elif days_since_last == 5:
                    points = s_d_5
                elif days_since_last == 6:
                    points = s_d_6
                elif days_since_last >= f_start_day:
                    a, b = (float(f_init_a), float(f_init_b))
                    current_a, current_b = (a, b)
                    if days_since_last == f_start_day:
                        points = current_a + current_b
                    elif days_since_last > f_start_day:
                        current_score_val = current_a + current_b
                        for _i in range(days_since_last - f_start_day):
                            next_val = current_a + current_b
                            current_a = current_b
                            current_b = next_val
                        points = current_b
                if days_since_last > 0 and b_divisor > 0:
                    bonus_points = days_since_last // b_divisor * b_val_group
                    points += bonus_points
            else:
                max_possible_days_absent = (date_to_predict - sorted_history[0]['date']).days if sorted_history else f_start_day + 10
                if max_possible_days_absent >= f_start_day:
                    a, b = (float(f_init_a), float(f_init_b))
                    for _i in range(max_possible_days_absent - f_start_day + 1):
                        c = a + b
                        a = b
                        b = c
                    points = b
                    if b_divisor > 0:
                        bonus_points = max_possible_days_absent // b_divisor * b_val_group
                        points += bonus_points
                else:
                    points = 0.0
            scores[num_str_format] = float(f'{points:.4g}')
        self._log('info', f'Prediction finished for {date_to_predict}. Generated {len(scores)} scores.')
        return scores