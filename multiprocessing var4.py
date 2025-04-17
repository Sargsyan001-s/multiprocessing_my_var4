import multiprocessing
import random
import time
from collections import Counter
import logging
import psutil

# Настройка логирования
logging.basicConfig(
    filename='analyzer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Генерация случайного списка
def generate_random_list(size, min_value=1, max_value=100):
    return [random.randint(min_value, max_value) for _ in range(size)]

# Функция для вычисления наиболее часто встречаемого элемента
def most_common_element(data):
    counter = Counter(data)
    return counter.most_common(1)[0]

# Функция для вычисления наименее часто встречаемого элемента
def least_common_element(data):
    counter = Counter(data)
    return counter.most_common()[-1]

# Функция для вычисления суммы всех чисел
def sum_of_elements(data):
    time.sleep(5)  # Имитация долгой задачи
    return sum(data)

# Функция для вычисления среднего арифметического
def average_of_elements(data):
    return sum(data) / len(data)

# Функция для вычисления медианы
def median_of_elements(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        return sorted_data[n // 2]

# Основная функция обработки задач
def process_task(task_queue, result_queue, timeout=10):
    while not task_queue.empty():
        try:
            # Получаем задачу из очереди
            task_name, data = task_queue.get(timeout=1)
            start_time = time.time()
            logging.info(f"Начало выполнения задачи '{task_name}'.")

            # Выполняем задачу
            if task_name == "most_common":
                result = most_common_element(data)
            elif task_name == "least_common":
                result = least_common_element(data)
            elif task_name == "sum":
                result = sum_of_elements(data)
            elif task_name == "average":
                result = average_of_elements(data)
            elif task_name == "median":
                result = median_of_elements(data)
            else:
                result = None

            # Проверяем время выполнения
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout:
                logging.warning(f"Задача '{task_name}' заняла слишком много времени ({elapsed_time:.2f} сек). Возвращаем в очередь.")
                task_queue.put((task_name, data))  # Возвращаем задачу в очередь
            else:
                result_queue.put((task_name, result))
                logging.info(f"Задача '{task_name}' выполнена за {elapsed_time:.2f} секунд.")
        except Exception as e:
            logging.error(f"Ошибка при выполнении задачи: {e}")

# Сохранение результатов
def save_results(results, output_file):
    with open(output_file, 'w') as f:
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    logging.info("Результаты сохранены в файл.")

# Основная программа
if __name__ == "__main__":
    # Ввод данных от пользователя
    size = int(input("Введите количество элементов в списке: "))
    data = generate_random_list(size)
    logging.info(f"Сгенерирован список из {size} элементов.")

    # Определяем максимальное количество процессов
    cpu_count = multiprocessing.cpu_count()
    cpu_load = psutil.cpu_percent(interval=1) / 100
    max_processes = int(cpu_count * (1 - cpu_load))  # Учитываем загрузку процессора
    max_processes = max(1, max_processes)  # Минимум 1 процесс
    logging.info(f"Используется {max_processes} процессов (загрузка процессора: {cpu_load * 100:.1f}%).")

    # Очереди для задач и результатов
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    # Заполняем очередь задачами
    tasks = [
        ("most_common", data),
        ("least_common", data),
        ("sum", data),
        ("average", data),
        ("median", data)
    ]
    for task in tasks:
        task_queue.put(task)

    # Создаем пул процессов
    processes = []
    for _ in range(max_processes):
        process = multiprocessing.Process(target=process_task, args=(task_queue, result_queue))
        processes.append(process)
        process.start()

    # Ждём завершения всех процессов
    for process in processes:
        process.join()

    # Собираем результаты из очереди
    results = {}
    while not result_queue.empty():
        task_name, result = result_queue.get()
        results[task_name] = result

    # Сохраняем результаты в файл через фоновый процесс
    save_process = multiprocessing.Process(target=save_results, args=(results, "results.txt"))
    save_process.start()
    save_process.join()

    # Выводим результаты на экран
    print("\nРезультаты анализа:")
    for key, value in results.items():
        if key == "most_common":
            print(f"Наиболее часто встречаемый элемент: {value[0]} (встречается {value[1]} раз)")
        elif key == "least_common":
            print(f"Наименее часто встречаемый элемент: {value[0]} (встречается {value[1]} раз)")
        elif key == "sum":
            print(f"Сумма всех чисел: {value}")
        elif key == "average":
            print(f"Среднее арифметическое: {value:.2f}")
        elif key == "median":
            print(f"Медиана: {value}")