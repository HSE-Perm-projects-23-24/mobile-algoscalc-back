import os
from typing import Any, Union

from src.core.algorithm import Algorithm
from src.core.algorithm_builder import AlgorithmBuilder
from src.core import NO_ALGORITHMS_MSG, ALGORITHM_NOT_EXISTS_TEMPL


class AlgorithmCollection:
    """Класс представляет собой набор объектов класса Algorithm,
    созданных объектом класса AlgorithmBuilder.

    """
    def __init__(self, path_config: dict[str, str],
                 algorithm_config: dict[str, Union[str, int]],
                 log_config: dict[str, Any]):
        """Конструктор класса

        :param path_config: путь к каталогу с исходным кодом алгоритмов;
        :type path_config: str
        :param algorithm_config: парамеры для создаваемых алгоритмов;
        :type algorithm_config: dict[str, Any]
        :param log_config: конфигурация логирования;
        :type log_config: dict[str, Any]
        """
        self.__algorithms: dict[str, Algorithm] = {}
        self.__path_config = path_config
        builder = AlgorithmBuilder(path_config['definition_file_name'],
                                   path_config['function_file_name'],
                                   path_config['test_file_name'],
                                   path_config['json_schema_file_path'],
                                   algorithm_config, log_config)
        catalog_path = path_config['algorithms_catalog_path']
        for obj in os.listdir(catalog_path):
            alg_path = catalog_path + '/' + obj
            if os.path.isdir(alg_path):
                alg = builder.build_algorithm(alg_path)
                self.__algorithms[alg.name] = alg
        if len(self.__algorithms) == 0:
            raise RuntimeError(NO_ALGORITHMS_MSG)

    def has_algorithm(self, algorithm_name: str) -> bool:
        """Проверяет наличие алгоритма с указанным именем.

        :param algorithm_name: имя алгоритма;
        :type algorithm_name: str
        :return: True при наличии алгоритма, иначе False.
        :rtype: bool
        """
        return algorithm_name in self.__algorithms

    def get_name_title_dict(self) -> dict[str, str]:
        """Возвращает словарь с уникальными именами алгоритмов в качестве
        ключей и названиями алгоритмов в качестве значений.

        :return: словарь с именами и названиями алгоритмов.
        :rtype: dict[str, Any]
        """
        return {name: alg.title for name, alg in self.__algorithms.items()}

    def get_algorithm(self, algorithm_name: str) -> Algorithm:
        """Возвращает объект класса Algorithm с указанным именем.

        :param algorithm_name: имя алгоритма;
        :type algorithm_name: str
        :return: объект класса Algorithm
        :rtype: Algorithm
        :raises ValueError: если алгоритм с указанным именем отсутствует;
        """
        if algorithm_name not in self.__algorithms:
            raise ValueError(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        return self.__algorithms[algorithm_name]

    def get_algorithm_result(self, algorithm_name: str,
                             params: dict[str, Any]) -> dict[str, Any]:
        """Возвращает результат выполнения алгоритма с указанным именем.

        :param algorithm_name: имя алгоритма;
        :type algorithm_name: str
        :param params: значения входных данных для выполнения алгоритма.
            Словарь, где ключи - имена входных данных, значения - фактические
            значения входных данных.
        :type params: dict[str, Any]
        :return: результат выполнения алгоритма. Словарь, где ключи - имена
            выходных данных, значения - рассчитанные значения выходных данных.
        :rtype: Algorithm
        :raises ValueError: если алгоритм с указанным именем отсутствует;
        :raises KeyError: если во входных или выходных данных отсутствует
            необходимый или имеется лишний элемент;
        :raises TimeoutError: если закончилось время, отведенное для
            выполнения алгоритма;
        :raises RuntimeError: при возникновении ошибки при выполнении.
        """
        if algorithm_name not in self.__algorithms:
            raise ValueError(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        return self.__algorithms[algorithm_name].execute(params)
    
    def get_algorithm_file_path(self, algorithm_name: str) -> str:
        """Возвращает строчный путь файла алгоритма с указанным именем.

        :param algorithm_name: имя алгоритма;
        :type algorithm_name: str
        :return: строка - путь к файлу алгоритма
        :rtype: str
        :raises ValueError: если алгоритм с указанным именем отсутствует;
        :raises RuntimeError: если 
        """
        if algorithm_name not in self.__algorithms:
            raise ValueError(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        
        alg_file_path = '/'.join([
            self.__path_config['algorithms_catalog_path'],
            algorithm_name,
            self.__path_config['function_file_name']
        ])
        return alg_file_path
