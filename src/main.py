"""Реализация API для онлайн-калькулятора с использованием фреймворка FastAPI.
"""

import os
import json
import logging.config
from fastapi import FastAPI
from fastapi.responses import FileResponse
from fastapi.middleware.cors import CORSMiddleware

from src.core.algorithm_collection import AlgorithmCollection, \
    ALGORITHM_NOT_EXISTS_TEMPL
from src.api_models import AlgorithmTitle, Algorithms, DataDefinition, \
    AlgorithmDefinition, Data, Parameters, Outputs, AnswerOutputs, \
    AnswerAlgorithmDefinition
from src import APP_CONFIG_FILE_PATH, LOG_CONFIG_FILE_PATH, \
    PATH_CONFIG, ALGORITHM_CONFIG, IS_TEST_APP, EXECUTE_TIMEOUT, \
    ALGORITHMS_ENDPOINT, TIME_OVER_MSG

if os.path.exists('../' + LOG_CONFIG_FILE_PATH):
    os.chdir('..')
with open(LOG_CONFIG_FILE_PATH, 'r') as log_conf_file:
    log_config = json.load(log_conf_file)
file_path = None
try:
    file_path = log_config["handlers"]["file_handler"]["filename"]
except KeyError:
    pass
if file_path:
    folder = os.path.split(file_path)[0]
    if not os.path.isdir(folder):
        os.mkdir(folder)
logging.config.dictConfig(log_config)
logger = logging.getLogger(__name__)
logger.info('Start app')

with open(APP_CONFIG_FILE_PATH, 'r') as conf_file:
    config = json.load(conf_file)
path_config = config[PATH_CONFIG]
algorithm_config = config[ALGORITHM_CONFIG]
if bool(os.environ.get(IS_TEST_APP)):
    algorithm_config[EXECUTE_TIMEOUT] = 0

algorithms = AlgorithmCollection(path_config, algorithm_config, log_config)

app = FastAPI()
web_config = config['web_config']
app.add_middleware(
    CORSMiddleware,
    allow_origins=web_config['cors']['origins'],
    allow_credentials=web_config['cors']['credentials'],
    allow_methods=web_config['cors']['methods'],
    allow_headers=web_config['cors']['headers']
)


@app.get(ALGORITHMS_ENDPOINT)
async def get_algorithms() -> Algorithms:
    """Возвращает список имеющихся алгоритмов.

    :return: список имеющихся алгоритмов.
    :rtype: Algorithms
    """
    logger.info('Request received')
    res = Algorithms(algorithms=[])
    for name, title in algorithms.get_name_title_dict().items():
        res.algorithms.append(AlgorithmTitle(name=name, title=title))
    return res


@app.get(ALGORITHMS_ENDPOINT + '/{algorithm_name}')
async def get_algorithm(algorithm_name: str) -> AnswerAlgorithmDefinition:
    """Возвращает описание выбранного алгоритма.

    :param algorithm_name: имя алгоритма;
    :type algorithm_name: str
    :return: Описание алгоритма.
    :rtype: AnswerAlgorithmDefinition
    """
    logger.info(f'Request received. algorithm_name: {algorithm_name}')
    answer = AnswerAlgorithmDefinition()
    if not algorithms.has_algorithm(algorithm_name):
        logger.warning(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        answer.errors = ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name)
        return answer
    try:
        alg = algorithms.get_algorithm(algorithm_name)
        params = []
        outputs = []
        for param in alg.parameters:
            params.append(
                DataDefinition(name=param.name, title=param.title,
                               description=param.description,
                               data_type=str(param.data_type),
                               data_shape=str(param.data_shape),
                               default_value=param.default_value))
        for output in alg.outputs:
            outputs.append(
                DataDefinition(name=output.name, title=output.title,
                               description=output.description,
                               data_type=str(output.data_type),
                               data_shape=str(output.data_shape),
                               default_value=output.default_value))
        alg_def = AlgorithmDefinition(name=alg.name, title=alg.title,
                                      description=alg.description,
                                      parameters=params, outputs=outputs)
        answer.result = alg_def
    except Exception as error:
        logger.warning(str(error))
        answer.errors = str(error)
    return answer


@app.get(ALGORITHMS_ENDPOINT + '/{algorithm_name}/download')
async def get_algorithm_file(algorithm_name: str) -> FileResponse:
    """Возвращает файл алгоритма по его имени.
    
    :param algorithm_name: имя алгоритма;
    :type algorithm_name: str
    :return: Файл алгоритма.
    :rtype: FileResponse
    """
    logger.info(f'Request received. algorithm_name: {algorithm_name}')

    if not algorithms.has_algorithm(algorithm_name):
        logger.warning(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        return {"error": ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name)}
    try:
        file_path = algorithms.get_algorithm_file_path(algorithm_name)
        return FileResponse(file_path)
    except Exception as error:
        logger.warning(str(error))
        return {"error": str(error)}


@app.post(ALGORITHMS_ENDPOINT + '/{algorithm_name}')
async def get_algorithm_result(algorithm_name: str, parameters: Parameters) \
        -> AnswerOutputs:
    """Возвращает результат выполнения выбранного алгоритма.

    :param algorithm_name: имя алгоритма;
    :type algorithm_name: str
    :param parameters: значения входных данных для выполнения алгоритма.
    :type parameters: Parameters
    :return: результат выполнения выбранного алгоритма
    :rtype: AnswerOutputs
    """
    logger.info(f'Request received. algorithm_name: {algorithm_name}, '
                f'parameters: {parameters}')
    answer = AnswerOutputs()
    if not algorithms.has_algorithm(algorithm_name):
        logger.warning(ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name))
        answer.errors = ALGORITHM_NOT_EXISTS_TEMPL.format(algorithm_name)
        return answer
    params = parameters.get_params_to_execute()
    try:
        results = algorithms.get_algorithm_result(algorithm_name, params)
        outputs = []
        for name, value in results.items():
            outputs.append(Data(name=name, value=value))
        answer.result = Outputs(outputs=outputs)
    except TimeoutError:
        logger.warning(TIME_OVER_MSG)
        answer.errors = TIME_OVER_MSG
    except Exception as error:
        logger.warning(str(error))
        answer.errors = str(error)
    return answer
