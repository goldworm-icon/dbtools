import os

import pkg_resources

DIR_PATH = os.path.abspath(os.path.dirname(__file__))
PROJECT_ROOT_PATH = os.path.abspath(os.path.join(DIR_PATH, '..', '..'))


def get_preptools_version() -> str:
    """Get version of preptools.
    The location of the file that holds the version information is different when packaging and when executing.
    :return: version of tbears.
    """
    try:
        version = pkg_resources.get_distribution('preptools').version
    except pkg_resources.DistributionNotFound:
        version_path = os.path.join(PROJECT_ROOT_PATH, 'VERSION')
        with open(version_path, mode='r') as version_file:
            version = version_file.read()
    except:
        version = 'unknown'
    return version
