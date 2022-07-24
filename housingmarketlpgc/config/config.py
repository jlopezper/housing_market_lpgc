import pathlib
import housingmarketlpgc


# root
PACKAGE_ROOT = pathlib.Path(housingmarketlpgc.__file__).resolve().parent
DATASET_DIR = PACKAGE_ROOT / "data"
PACKAGE_NAME = "housingmarketlpgc"
