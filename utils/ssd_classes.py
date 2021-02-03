"""ssd_classes.py

"""

COCO_CLASSES_LIST = [
    'background',  # was 'unlabeled'
    'digger',
    ]

def get_cls_dict(model):
    """Get the class ID to name translation dictionary."""
    if model == 'coco':
        cls_list = COCO_CLASSES_LIST
    else:
        raise ValueError('Bad model name')
    return {i: n for i, n in enumerate(cls_list)}
