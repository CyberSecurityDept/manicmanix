import os
# UPLOAD = "test-dir/"

# file_directory = os.path.dirname(os.path.abspath(__file__))

# file_path = os.path.dirname(file_directory)

# check_path = os.path.join(file_path, UPLOAD)

# # create_file = os.makedirs(os.path.join(file_path, "uploaded_files/"))



# APP_PATH = os.path.abspath(__file__)
# APP_HOME = os.path.dirname(APP_PATH)
# APP_ROOT = os.path.dirname(APP_HOME)
# UPLOAD_FOLDER = os.path.join(APP_ROOT, UPLOAD_PATH)

UPLOAD_DIR = "uploaded_files/"

BASE_FOLDER = os.path.dirname(os.path.abspath(__file__))

# nentuin root parent dari folder app
ROOT_FOLDER = os.path.dirname(BASE_FOLDER)


UPLOAD_FOLDER = os.path.join(ROOT_FOLDER, UPLOAD_DIR)
print(UPLOAD_FOLDER)
