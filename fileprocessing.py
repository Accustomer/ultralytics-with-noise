import os
import cv2
import random
import shutil
from voc_yolo import parse_voc, xyxy2xywh, write_voc
 
 
def splitBack():
    src_dir = '/data/LongAoTian/frameworks/ultralytics-with-noise/data/horse/back-images'
    dst_dirs = ['-'.join((src_dir, n)) for n in ('train', 'test')]
    for p in dst_dirs:
        if not os.path.exists(p):
            os.mkdir(p)
            
    file_names = os.listdir(src_dir)
    random.shuffle(file_names)
    train_num = round(0.5 * len(file_names))
    for fn in file_names[:train_num]:
        src_path = '/'.join((src_dir, fn))
        dst_path = '/'.join((dst_dirs[0], fn))
        if not os.path.exists(dst_path):
            os.rename(src_path, dst_path)
    for fn in file_names[train_num:]:
        src_path = '/'.join((src_dir, fn))
        dst_path = '/'.join((dst_dirs[1], fn))
        if not os.path.exists(dst_path):
            os.rename(src_path, dst_path)
                                  
    
def linkImages():
    data_root = '/data/LongAoTian/frameworks/ultralytics-with-noise/data/horse'
    src_names = ('fore-images', 'back-images-train')
    dst_dir = '/'.join((data_root, 'images'))
    if not os.path.exists(dst_dir):
        os.mkdir(dst_dir)
    for sn in src_names:
        src_dir = '/'.join((data_root, sn))
        file_names = os.listdir(src_dir)
        for fn in file_names:
            src_path = '/'.join((src_dir, fn))
            dst_path = '/'.join((dst_dir, fn))
            if not os.path.exists(dst_path):
                os.symlink(src_path, dst_path)
 
 
def splitTrainValWithNoise():
    data_root = 'data/horse'
    images_dir = '/'.join((data_root, 'images'))
    labels_dir = '/'.join((data_root, 'labels'))
    classes = ("horse", )

    file_names = os.listdir(images_dir)
    fore_names, back_names = [], []
    for fn in file_names:
        pure_name = ".".join(fn.split(".")[:-1])
        label_path = '/'.join((labels_dir, pure_name + ".txt"))
        if not os.path.exists(label_path):
            continue
        with open(label_path, "r") as f:
            back_flags = [int(line.split(" ")[0]) == -1 for line in f.read().strip().splitlines()]
        if any(back_flags):
            if all(back_flags):
                back_names.append(fn)
            else:
                print("There are some objects at background image")
        else:
            fore_names.append(fn)

    train_name = 'train-with-noise.txt'
    valid_name = 'valid-with-noise.txt'
    train_path = '/'.join((data_root, train_name))
    valid_path = '/'.join((data_root, valid_name))
    setting_path = '/'.join((data_root, "horse-with-noise.yaml"))
    train_num = round(0.8 * len(fore_names))
    random.shuffle(fore_names)
    with open(train_path, 'w') as f:
        f.write("\n".join(["/".join((images_dir, fn)) for fn in fore_names[:train_num] + back_names]))
    with open(valid_path, 'w') as f:
        f.write("\n".join(["/".join((images_dir, fn)) for fn in fore_names[train_num:]]))
    with open(setting_path, "w") as f:
        f.write(f"train: {train_name}\n" 
                f"val: {valid_name}\n" 
                f"nc: {len(classes)}\n" 
                f"names: [{', '.join(classes)}]\n"
                )
        
    train_name = 'train-without-noise.txt'
    valid_name = 'valid-without-noise.txt'
    train_path = '/'.join((data_root, train_name))
    valid_path = '/'.join((data_root, valid_name))
    setting_path = '/'.join((data_root, "horse-without-noise.yaml"))
    with open(train_path, 'w') as f:
        f.write("\n".join(["/".join((images_dir, fn)) for fn in fore_names[:train_num]]))
    with open(valid_path, 'w') as f:
        f.write("\n".join(["/".join((images_dir, fn)) for fn in fore_names[train_num:]]))
    with open(setting_path, "w") as f:
        f.write(f"train: {train_name}\n" 
                f"val: {valid_name}\n" 
                f"nc: {len(classes)}\n" 
                f"names: [{', '.join(classes)}]\n"
                )
       
       
if __name__ == '__main__':
    # splitBack()
    # linkImages()
    splitTrainValWithNoise()
       