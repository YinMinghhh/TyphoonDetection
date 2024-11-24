import os
import shutil
import xml.etree.ElementTree as ET

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
    images_path = os.path.join(target_path, 'images')
    os.makedirs(images_path)
    labels_path = os.path.join(target_path, 'labels')
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

if __name__ == '__main__': 
    source_path = '..\data'
    target_path = '..\dataset'
    source2yolo(source_path, target_path)
