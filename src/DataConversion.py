import os
import shutil
import xml.etree.ElementTree as ET
import random

classes = []

def get_yolo_box(size, box): 
    dw = 1. / size[0]
    dh = 1. / size[1]
    x = (box[0] + box[2]) / 2 * dw
    y = (box[1] + box[3]) / 2 * dh
    w = (box[2] - box[0]) * dw
    h = (box[3] - box[1]) * dh
    return (x, y, w, h)

def source2yolo(source_path, target_path): 
    if (os.path.exists(target_path)):
        shutil.rmtree(target_path)

    images_path = os.path.join(target_path, 'images')
    labels_path = os.path.join(target_path, 'labels')


    if (not os.path.exists(images_path)):
        os.makedirs(images_path)
    if (not os.path.exists(labels_path)):
        os.makedirs(labels_path)


    for folder in os.listdir(source_path):
        folder_path = os.path.join(source_path, folder)
        for file in os.listdir(folder_path): 
            file_path = os.path.join(folder_path, file)
            
            _, file_extension = os.path.splitext(file)

            if file_extension == '.png': 
                out_file = os.path.join(images_path, file)
                shutil.copyfile(file_path, out_file)

            elif file_extension == '.xml': 
                root = ET.parse(file_path).getroot()
                size = root.find('size')

                # Since every image is the same size, it dosen't seem necessary to reload everytime
                w = int(size.find('width').text)
                h = int(size.find('height').text)

                out_file_path = os.path.join(labels_path, file.replace('xml', 'txt'))
                out_file = open(out_file_path, 'w')

                for obj in root.iter('object'): 
                    name = obj.find('name').text
                    if name not in classes: 
                        classes.append(name)
                    id = classes.index(name)

                    bndbox = obj.find('bndbox')
                    box = [float(bndbox.find('xmin').text), float(bndbox.find('ymin').text), float(bndbox.find('xmax').text), float(bndbox.find('ymax').text)]
                    yolo_box = get_yolo_box((w, h), box)

                    out_file.write(str(id) + ' ' + ' '.join(str(num) for num in yolo_box) + '\n')

            else:
                pass

def data_split(train_path, val_path, test_path):
    '''
    把 train_path 中随机选择的
    '''
    if (os.path.exists(val_path)):
        shutil.rmtree(val_path)
    if (os.path.exists(test_path)): 
        shutil.rmtree(test_path)

    val_images_path = os.path.join(val_path, 'images')
    val_labels_path = os.path.join(val_path, 'labels')
    test_images_path = os.path.join(test_path, 'images')
    test_labels_path = os.path.join(test_path, 'labels')

    os.makedirs(val_images_path)
    os.makedirs(val_labels_path)
    os.makedirs(test_images_path)
    os.makedirs(test_labels_path)

    train_images_path = os.path.join(train_path, 'images')
    train_labels_path = os.path.join(train_path, 'labels')

    # val
    image_file_list = os.listdir(train_images_path)
    print('Count of total files: ' + str(len(image_file_list)))
    val_collection = random.sample(image_file_list, k=int(len(image_file_list) * 0.2))
    print('Count of val files: ' + str(int(len(val_collection))))

    for file in val_collection: 
        shutil.move(os.path.join(train_images_path, file), val_images_path)
        shutil.move(os.path.join(train_labels_path, file.replace('png', 'txt')), val_labels_path)

    # test
    image_file_list = os.listdir(train_images_path)
    test_collection = random.sample(image_file_list, k=int(len(val_collection)))
    print('Count of test files: ' + str(int(len(test_collection))))

    for file in test_collection: 
        shutil.move(os.path.join(train_images_path, file), test_images_path)
        shutil.move(os.path.join(train_labels_path, file.replace('png', 'txt')), test_labels_path)



if __name__ == '__main__': 
    source_path = '..\data'
    target_path = '..\dataset'
    source2yolo(source_path, os.path.join(target_path, 'train'))
    data_split(os.path.join(target_path, 'train'), os.path.join(target_path, 'val'), os.path.join(target_path, 'test'))
