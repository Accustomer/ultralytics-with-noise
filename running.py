from ultralytics import YOLO


def detectDemo():
    model_names = ('horse-without-noise', 'horse-with-noise')
    data_names = ('back-images-train', 'back-images-test')
    dst_names = ('h-wo-n-train', 'h-wo-n-test', 'h-w-n-train', 'h-w-n-test')
    
    k = 0
    num_dets = []
    for mn in model_names:
        model = YOLO(f"runs/detect/{mn}/weights/best.pt")
        for dn in data_names:            
            results = model.predict(
                source=f"data/horse/{dn}", 
                stream=True, 
                save=True,
                save_txt=False,
                save_conf=True, 
                device="0",
                imgsz=640,
                conf=0.4,
                iou=0.5,
                max_det=100, 
                name=dst_names[k]
            )
            n_dets = 0
            for res in results:
                n_dets += res.boxes.xywh.shape[0]
            num_dets.append(n_dets)
            k += 1
            
    k = 0
    for mn in model_names:
        for dn in data_names: 
            print(f"False detection {mn} + {dn} : {num_dets[k]}")
            k += 1


def trainHorse():
    model = YOLO("weights/yolov8n.pt")
    model.train(
        data="data/horse/horse-without-noise.yaml", 
        epochs=150,
        batch=128,
        imgsz=640,
        device='0',
        name="horse-without-noise", 
        cache=True, 
        close_mosaic=0,
        workers=1, 
        exist_ok=False,  # overwrite
        patience=0,     # early stop
        optimizer='AdamW', # optimizer to use, choices=['SGD', 'Adam', 'AdamW', 'RMSProp']
        momentum=0.937,  # SGD momentum/Adam beta1
        lr0=0.0001,  # initial learning rate (SGD=1E-2, Adam=1E-3)
        lrf=0.01,  # final OneCycleLR learning rate (lr0 * lrf)
        weight_decay=0.0005,  # optimizer weight decay 5e-4
        warmup_epochs=3.0,  # warmup epochs (fractions ok)
        warmup_momentum=0.8,  # warmup initial momentum
        warmup_bias_lr=0.1,  # warmup initial bias lr
        box=7.5,  # box loss gain
        cls=0.5,  # cls loss gain (scale with pixels)
        dfl=1.5,  # dfl loss gain
        label_smoothing=0.0,
        seed=8888,
        nbs=64,  # nominal batch size
        hsv_h=0.03,  # image HSV-Hue augmentation (fraction)    # 0.015
        hsv_s=0.7,  # image HSV-Saturation augmentation (fraction)
        hsv_v=0.4,  # image HSV-Value augmentation (fraction)
        degrees=0.0,  # image rotation (+/- deg)
        translate=0.1,  # image translation (+/- fraction)
        scale=0.5,  # image scale (+/- gain)
        shear=0.1,  # image shear (+/- deg)
        perspective=0.0,  # image perspective (+/- fraction), range 0-0.001
        flipud=0,  # image flip up-down (probability)
        fliplr=0.5,  # image flip left-right (probability)
        mosaic=1.0,  # image mosaic (probability)
        mixup=0.0,  # image mixup (probability)
        copy_paste=0.0  # segment copy-paste (probability)
    )


def evalHorse():
    model = YOLO("runs/detect/horse-without-noise/weights/best.pt")
    model.val(
        data='data/horse/horse-without-noise.yaml',
        device='0',
        half=True,
        plots=True,
        batch=64, 
        name='horse-without-noise-val'
    )


if __name__ == '__main__':
    detectDemo()
    # trainHorse()
    # evalHorse()
