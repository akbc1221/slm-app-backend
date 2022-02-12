import numpy as np


def object_serializer(obj):
    return {
        'id': obj.id,
        "createdAt": obj.createdAt,
        "outcome": obj.outcome,
        "inputs": obj.inputs
    }


def convert_for_model(data):
    return np.array([
        data['scanSpeed'], data['hatchDistance'], data['laserPower'],
        data['layerThickness']
    ]).reshape(1, -1)
