# Modification Record
1. Add lines to function **ultralytics/data/base.py -- BaseDataset.__init__**:
``` Python
## Additional attributes
self.use_mosaic = augment and hyp.mosaic > 0
self.foreground_indexes = []
```
2. Change function **ultralytics/data/utils.py -- verify_image_label_with_background**:
``` Python
# Old: 
assert (lb >= 0).all(), f'negative label values {lb[lb < 0]}'
# New (-1: background, [0, num_cls): classes):
assert (lb >= -1).all(), f'negative label values {lb[lb < 0]}'
```
3. Add function **ultralytics/data/dataset.py -- YOLODataset.\_\_len__**:
``` Python
def __len__(self):
    if self.use_mosaic:
        return len(self.labels)
    else:
        return len(self.foreground_indexes)
```
4. Add function **ultralytics/data/dataset.py -- YOLODataset.\_\_getitem__**:
``` Python
def __getitem__(self, index):
    if self.use_mosaic:
        return self.transforms(self.get_image_and_label(index))
    else:
        return self.transforms(self.get_image_and_label(self.foreground_indexes[index]))
```
5. Add lines to function **ultralytics/data/dataset.py -- YOLODataset.get_labels**:
``` Python
# Get foreground index
self.foreground_indexes = []
for i, lb in enumerate(labels):
    if any(lb['cls'] < 0):
        continue
    self.foreground_indexes.append(i)
```
6. Add line to function **ultralytics/data/dataset.py -- YOLODataset.close_mosaic**:
``` Python
self.use_mosaic = False
```
7. Add function to **ultralytics/utils/instance.py -- Bboxes.set_bboxes**:
``` Python
def set_bboxes(self, new_bboxes):
    self.bboxes = new_bboxes
```
8. Add function to **ultralytics/utils/instance.py -- Instances.set_bboxes**:
``` Python
def set_bboxes(self, new_bboxes):
    self._bboxes.set_bboxes(new_bboxes)
```
9. Add lines to function **ultralytics/data/augment.py -- BaseMixTransform.\_\_call__**:
``` Python
# Remove background 
coord = np.where(labels['cls'] >= 0)[0]
labels['cls'] = labels['cls'][coord]
labels['instances'].set_bboxes(labels['instances'].bboxes[coord])
if len(labels['instances'].segments):
    labels['instances'].segments = labels['instances'].segments[coord]
```
10. Change function **ultralytics/data/augment.py -- Mosaic.get_indexes**:
``` Python
# Old
def get_indexes(self, buffer=True):
    """Return a list of random indexes from the dataset."""
    if buffer:  # select images from buffer
        return random.choices(list(self.dataset.buffer), k=self.n - 1)
    else:  # select any images
        return [random.randint(0, len(self.dataset) - 1) for _ in range(self.n - 1)]
# New 
def get_indexes(self):
    """Return a list of random indexes from the dataset."""
    if len(self.dataset.foreground_indexes) < len(self.dataset):
        return [random.choice(self.dataset.foreground_indexes)] + [random.randint(0, len(self.dataset) - 1) for _ in range(self.n - 2)]
    else:
        return [random.randint(0, len(self.dataset) - 1) for _ in range(self.n - 1)]
```
11. Change function **ultralytics/data/augment.py -- MixUp.get_indexes**:
``` Python
# Old
def get_indexes(self):
    """Get a random index from the dataset."""
    return random.randint(0, len(self.dataset) - 1)
# New 
def get_indexes(self):
    """Get a random index from the dataset."""
    if len(self.dataset.foreground_indexes) < len(self.dataset):
            return random.choice(self.dataset.foreground_indexes)
    else:
        return random.randint(0, len(self.dataset) - 1)
```
12. Comment out all "Buffer thread for mosaic images".
- **ultralytics/data/base.py -- BaseDataset.\_\_init__**
- **ultralytics/data/base.py -- BaseDataset.load_image**
- **ultralytics/models/rtdetr/val.py -- RTDETRDataset.load_image**
13. Change function **ultralytics/utils/__init__.py -- SettingsManager.\_\_init__** (Optional. Personal habit
):
``` Python
# Old
super().__init__(copy.deepcopy(self.defaults))
# New
self.update(copy.deepcopy(self.defaults))
```
14. Change function **ultralytics/data/utils.py -- check_det_dataset** (Optional. Personal habit):
``` Python
# Old
path = Path(extract_dir or data.get('path') or Path(data.get('yaml_file', '')).parent)  # dataset root
if not path.is_absolute():
    path = (DATASETS_DIR / path).resolve()
# New
path = Path(extract_dir or data.get('path') or Path(data.get('yaml_file', '')).parent.parent)  # dataset root
if not path.is_absolute():
    path = (os.getcwd() / path).resolve()
```

All changes can be found by keys:
- PERSONAL_HABIT_CHANGE
- NOISY_BACKGROUND_CHANGE

