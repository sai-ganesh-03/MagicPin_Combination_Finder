import time
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)

def find_combinations(items, target):
    max_combinations = 10000

    def _find_combinations(idx, current_sum, current_combination, combination_count):
        nonlocal max_combinations
        if combination_count[0] >= max_combinations:
            return True
        if current_sum >= target and current_sum <= target + 10:
            result.append((current_combination, current_sum))
            combination_count[0] += 1
            return combination_count[0] >= max_combinations
        if current_sum > target or idx >= len(items):
            return False
        # Include the current item
        if _find_combinations(idx + 1, current_sum + items[idx]['mrp'], current_combination + [items[idx]], combination_count):
            return True
        # Exclude the current item
        if _find_combinations(idx + 1, current_sum, current_combination, combination_count):
            return True
        return False

    start_combinations = time.time()
    result = []
    combination_count = [0]
    if _find_combinations(0, 0, [], combination_count):
        logging.info("Combination limit reached: %d", max_combinations)
    end_combinations = time.time()
    combinations_time = end_combinations - start_combinations
    logging.info("Time taken by find_combinations function: %.2f seconds", combinations_time)
    return result
