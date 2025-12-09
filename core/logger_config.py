"""
Logger Configuration
    Description:
        Core script for initializing logging and shared utilities
"""
import logging

logger = logging.getLogger(__name__)


def setup_logging(level=logging.INFO)-> None:
    """Setup logging configuration for the entire application"""
    logging.basicConfig(
        level=level,
        format='[%(asctime)s][%(name)s][%(levelname)s] %(message)s',
        datefmt='%H:%M:%S',
        force=True
    )


if __name__ == "__main__":
    setup_logging()
    logger.info('Logging setup complete')