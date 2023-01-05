import math
import os
import os.path
import shutil
from os.path import isfile, join
from uuid import UUID

from PIL import Image


class ArgumentError(Exception):
    pass


def prepare_folder(folder_path: str):
    if os.path.exists(folder_path) is False:
        os.makedirs(folder_path)

    for filename in os.listdir(folder_path):
        file_path = os.path.join(folder_path, filename)
        if os.path.isfile(file_path) or os.path.islink(file_path):
            os.unlink(file_path)
        elif os.path.isdir(file_path):
            shutil.rmtree(file_path)

    return


def create_grid(inference_type: str, snowflake_id, res_x: int, res_y: int, count: int):
    # Code for creating an image grid is taken from StackOverflow, https://stackoverflow.com/questions/20038648/writting-a-file-with-multiple-images-in-a-grid
    folder_path = os.path.join("temp", inference_type, snowflake_id)

    files = [f for f in os.listdir(folder_path) if
             isfile(join(folder_path, f))]

    if len(files) == 0:
        return

    axis_size_x = math.ceil(math.sqrt(count))
    axis_size_y = axis_size_x
    while axis_size_x * axis_size_y > len(files):
        axis_size_y -= 1

    grid_res_x = axis_size_x * res_x
    grid_res_y = axis_size_y * res_y

    grid = Image.new('RGB', (grid_res_x, grid_res_y))

    index = 0
    is_exiting = False
    for j in range(0, grid_res_y, res_y):
        for i in range(0, grid_res_x, res_x):
            if index > len(files) - 1 and index != 0:
                is_exiting = True
                break
            im = Image.open(os.path.join(folder_path, files[index]))
            im.thumbnail((res_x, res_y))
            grid.paste(im, (i, j))
            index += 1

        if is_exiting:
            break

    grid.save(os.path.join(folder_path, "grid.jpg"))
