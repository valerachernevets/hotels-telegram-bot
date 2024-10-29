"""В этом модуле добавляем обработчик в логгер."""
from loguru import logger

logger.add('logs/test_logs.log', level='DEBUG',
           format='{time:YYYY-MM-DD at HH:mm:ss} {level} {name}.{function} - {message}',
           rotation='1000 KB', compression='zip')
