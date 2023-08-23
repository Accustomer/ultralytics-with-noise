import os
import codecs
from lxml import etree
from xml.etree import ElementTree
from xml.etree.ElementTree import Element, SubElement


class PascalVocWriter:

    def __init__(self, folder_name, filename, img_size, database_src='Unknown', local_img_path=None):
        self.folder_name = folder_name
        self.filename = filename
        self.database_src = database_src
        self.img_size = img_size
        self.box_list = []
        self.local_img_path = local_img_path
        self.verified = False

    def prettify(self, elem):
        """
            Return a pretty-printed XML string for the Element.
        """
        rough_string = ElementTree.tostring(elem, 'utf8')
        root = etree.fromstring(rough_string)
        return etree.tostring(root, pretty_print=True, encoding='utf-8').replace("  ".encode(), "\t".encode())
        # minidom does not support UTF-8
        # reparsed = minidom.parseString(rough_string)
        # return reparsed.toprettyxml(indent="\t", encoding=ENCODE_METHOD)

    def gen_xml(self):
        """
            Return XML root
        """
        # Check conditions
        if self.filename is None or \
                self.folder_name is None or \
                self.img_size is None:
            return None

        top = Element('annotation')
        if self.verified:
            top.set('verified', 'yes')

        folder = SubElement(top, 'folder')
        folder.text = self.folder_name

        filename = SubElement(top, 'filename')
        filename.text = self.filename

        if self.local_img_path is not None:
            local_img_path = SubElement(top, 'path')
            local_img_path.text = self.local_img_path

        source = SubElement(top, 'source')
        database = SubElement(source, 'database')
        database.text = self.database_src

        size_part = SubElement(top, 'size')
        width = SubElement(size_part, 'width')
        height = SubElement(size_part, 'height')
        depth = SubElement(size_part, 'depth')
        width.text = str(self.img_size[1])
        height.text = str(self.img_size[0])
        if len(self.img_size) == 3:
            depth.text = str(self.img_size[2])
        else:
            depth.text = '1'

        segmented = SubElement(top, 'segmented')
        segmented.text = '0'
        return top

    def add_bnd_box(self, x_min, y_min, x_max, y_max, name, difficult):
        bnd_box = {'xmin': x_min, 'ymin': y_min, 'xmax': x_max, 'ymax': y_max}
        bnd_box['name'] = name
        bnd_box['difficult'] = difficult
        self.box_list.append(bnd_box)

    def append_objects(self, top):
        for each_object in self.box_list:
            object_item = SubElement(top, 'object')
            name = SubElement(object_item, 'name')
            name.text = str(each_object['name'])
            pose = SubElement(object_item, 'pose')
            pose.text = "Unspecified"
            truncated = SubElement(object_item, 'truncated')
            if int(float(each_object['ymax'])) == int(float(self.img_size[0])) or (
                    int(float(each_object['ymin'])) == 1):
                truncated.text = "1"  # max == height or min
            elif (int(float(each_object['xmax'])) == int(float(self.img_size[1]))) or (
                    int(float(each_object['xmin'])) == 1):
                truncated.text = "1"  # max == width or min
            else:
                truncated.text = "0"
            difficult = SubElement(object_item, 'difficult')
            difficult.text = str(bool(each_object['difficult']) & 1)
            bnd_box = SubElement(object_item, 'bndbox')
            x_min = SubElement(bnd_box, 'xmin')
            x_min.text = str(each_object['xmin'])
            y_min = SubElement(bnd_box, 'ymin')
            y_min.text = str(each_object['ymin'])
            x_max = SubElement(bnd_box, 'xmax')
            x_max.text = str(each_object['xmax'])
            y_max = SubElement(bnd_box, 'ymax')
            y_max.text = str(each_object['ymax'])

    def save(self, target_file=None):
        root = self.gen_xml()
        self.append_objects(root)
        out_file = None
        if target_file is None:
            out_file = codecs.open(self.folder_name + self.filename + '.xml', 'w', encoding='utf-8')
        else:
            out_file = codecs.open(target_file, 'w', encoding='utf-8')

        prettify_result = self.prettify(root)
        out_file.write(prettify_result.decode('utf8'))
        out_file.close()


def xywh2xyxy(xywh, height, width):
    """ Convert xywh box to xyxy box """
    xmin = round((xywh[0] - xywh[2] / 2.0) * width)
    ymin = round((xywh[1] - xywh[3] / 2.0) * height)
    xmax = round((xywh[0] + xywh[2] / 2.0) * width)
    ymax = round((xywh[1] + xywh[3] / 2.0) * height)
    return xmin, ymin, xmax, ymax


def xyxy2xywh(xyxy, height, width):
    return [float(xyxy[0] + xyxy[2]) / 2 / width, 
            float(xyxy[1] + xyxy[3]) / 2 / height, 
            float(xyxy[2] - xyxy[0]) / width, 
            float(xyxy[3] - xyxy[1]) / height]


def parse_voc(voc_file):
    """ parse VOC xml, return xyxy box and image size """
    info_tree = ElementTree.parse(voc_file)
    size = info_tree.find('size')
    height = int(size.find('height').text)
    width = int(size.find('width').text)
    bboxes = []
    for obj in info_tree.findall('object'):
        bndbox = obj.find('bndbox')
        lbl = obj.find('name').text
        box_info = [lbl,
                    int(bndbox.find('xmin').text),
                    int(bndbox.find('ymin').text),
                    int(bndbox.find('xmax').text),
                    int(bndbox.find('ymax').text)]
        bboxes.append(box_info)
    return bboxes, height, width


def write_voc(voc_file, bboxes, height, width):
    pvw = PascalVocWriter(folder_name=os.path.dirname(voc_file)+os.path.sep, 
        filename='.'.join(os.path.split(voc_file)[-1].split('.')[:-1]), 
        img_size=(height, width))
    for bbox in bboxes:
        lbl = bbox[0]
        xyxy = bbox[1:]
        pvw.add_bnd_box(xyxy[0], xyxy[1], xyxy[2], xyxy[3], lbl, 1)            
    pvw.save()


def yolo2voc(yolo_file, voc_file, labels, height, width):
    """ Convert yolov5 label file to VOC format """
    pvw = PascalVocWriter(folder_name=os.path.dirname(voc_file)+os.path.sep, 
                        filename='.'.join(os.path.split(voc_file)[-1].split('.')[:-1]), 
                        img_size=(height, width))
    with open(yolo_file, 'r') as f:
        lines = f.read().strip().splitlines()
        for line in lines:
            yolo_info = line.split(' ')
            lbl = labels[int(yolo_info[0])]
            xywh = [float(v) for v in yolo_info[1:]]
            xyxy = xywh2xyxy(xywh, height, width)
            pvw.add_bnd_box(xyxy[0], xyxy[1], xyxy[2], xyxy[3], lbl, 1)
    pvw.save()



    