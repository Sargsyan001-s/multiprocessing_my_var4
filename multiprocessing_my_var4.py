import multiprocessing
import random
import time
from collections import Counter
import logging
import psutil

  
logging.basicConfig(
    filename='analyzer.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def generate_random_list(size, min_value=1, max_value=100):
    return [random.randint(min_value, max_value) for _ in range(size)]


def most_common_element(data):
    counter = Counter(data)
    return counter.most_common(1)[0]


def least_common_element(data):
    counter = Counter(data)
    return counter.most_common()[-1]


def sum_of_elements(data):
    time.sleep(5)  
    return sum(data)


def average_of_elements(data):
    return sum(data) / len(data)


def median_of_elements(data):
    sorted_data = sorted(data)
    n = len(sorted_data)
    if n % 2 == 0:
        return (sorted_data[n // 2 - 1] + sorted_data[n // 2]) / 2
    else:
        return sorted_data[n // 2]


def process_task(task_queue, result_queue, timeout=3, max_retries=3):
    retries = {}
    while not task_queue.empty():
        try:
            task_name, data = task_queue.get(timeout=1)
            start_time = time.time()
            logging.info(f"Начало выполнения задачи '{task_name}'.")

            
            if task_name not in retries:
                retries[task_name] = 0
            retries[task_name] += 1

            
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

            
            elapsed_time = time.time() - start_time
            if elapsed_time > timeout and retries[task_name] <= max_retries:
                logging.warning(f"Задача '{task_name}' заняла слишком много времени ({elapsed_time:.2f} сек). Возвращаем в очередь.")
                task_queue.put((task_name, data))  
                logging.info(f"Задача '{task_name}' добавлена обратно в очередь (попытка {retries[task_name]}).")
            else:
                result_queue.put((task_name, result))
                logging.info(f"Задача '{task_name}' выполнена за {elapsed_time:.2f} секунд.")
        except Exception as e:
            logging.error(f"Ошибка при выполнении задачи: {e}")


def save_results(results, output_file):
    with open(output_file, 'w') as f:
        for key, value in results.items():
            f.write(f"{key}: {value}\n")
    logging.info("Результаты сохранены в файл.")


if __name__ == "__main__":
    
    size = int(input("Введите количество элементов в списке: "))
    data = generate_random_list(size)
    logging.info(f"Сгенерирован список из {size} элементов.")

    
    cpu_count = multiprocessing.cpu_count()
    cpu_load = psutil.cpu_percent(interval=1) / 100
    max_processes = int(cpu_count * (1 - cpu_load))  
    max_processes = max(1, max_processes)  
    logging.info(f"Используется {max_processes} процессов (загрузка процессора: {cpu_load * 100:.1f}%).")

    
    task_queue = multiprocessing.Queue()
    result_queue = multiprocessing.Queue()

    
    tasks = [
        ("most_common", data),
        ("least_common", data),
        ("sum", data),
        ("average", data),
        ("median", data)
    ]
    for task in tasks:
        task_queue.put(task)

    
    processes = []
    for _ in range(max_processes):
        process = multiprocessing.Process(target=process_task, args=(task_queue, result_queue))
        processes.append(process)
        process.start()

   
    for process in processes:
        process.join()

    
    results = {}
    while not result_queue.empty():
        task_name, result = result_queue.get()
        results[task_name] = result
        logging.info(f"Результат задачи '{task_name}' добавлен в словарь результатов.")

    
    save_process = multiprocessing.Process(target=save_results, args=(results, "results.txt"))
    save_process.start()
    save_process.join()

    
    print("\nРезультаты анализа:")
    for key in ["most_common", "least_common", "sum", "average", "median"]:
        if key in results:
            value = results[key]
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
        else:
            print(f"Результат для задачи '{key}' не найден.")