import numpy as np


def object_serializer(obj):
    return {
        'id': obj.id,
        "createdAt": obj.createdAt,
        "outcome": obj.outcome,
        "inputs": obj.inputs,
        "starred": obj.starred,
        "tags": obj.tags
    }


def convert_for_model(data):
    return np.array([
        data['scanSpeed'], data['hatchDistance'], data['laserPower'],
        data['layerThickness']
    ]).reshape(1, -1)
