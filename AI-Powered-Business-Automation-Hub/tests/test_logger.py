import logging

from src.logger import get_logger


def test_logger_does_not_duplicate_handlers(tmp_path):
    logger_name = "test_logger_no_duplicates"
    logger = get_logger(logger_name, tmp_path)
    second_logger = get_logger(logger_name, tmp_path)

    assert second_logger is logger
    assert len(logger.handlers) == 2
    assert any(isinstance(handler, logging.FileHandler) for handler in logger.handlers)
