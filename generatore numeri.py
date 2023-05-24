import random

def random_number_generator():
    min_value = 1000
    max_value = 5000
    min_difference = 100
    numbers = set()

    while len(numbers) < 300:
        num = random.randint(min_value // 100, max_value // 100) * 100
        if all(abs(num - existing) >= min_difference for existing in numbers):
            numbers.add(num)
            yield num
    print(numbers)

random_numbers = list(random_number_generator())

random_numbers
