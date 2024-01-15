from Pyro5.api import config, register_class_to_dict, register_dict_to_class
from docker.models.containers import ContainerCollection
from docker.models.resource import Model
from docker.models.images import ImageCollection

# use serpent
config.SERIALIZER = "serpent"


# register the special serialization hooks
def containerCollection_class_to_dict(obj):
    # print("{serializer hook, converting to dict: %s}" % obj)
    return {
        "__class__": "ContainerCollection",
        # "number-attribute": obj.number
    }


def containerCollection_dict_to_class(classname, d):
    # print("{deserializer hook, converting to class: %s}" % d)
    return ContainerCollection()


register_dict_to_class("ContainerCollection", containerCollection_dict_to_class)
register_class_to_dict(ContainerCollection, containerCollection_class_to_dict)


def model_class_to_dict(obj):
    # print("{serializer hook, converting to dict: %s}" % obj)
    return {
        "__class__": "Model",
        # "number-attribute": obj.number
    }


def model_dict_to_class(classname, d):
    # print("{deserializer hook, converting to class: %s}" % d)
    return Model()


register_dict_to_class("Model", model_dict_to_class)
register_class_to_dict(Model, model_class_to_dict)


def ImageCollection_class_to_dict(obj):
    # print("{serializer hook, converting to dict: %s}" % obj)
    return {
        "__class__": "ImageCollection",
        # "number-attribute": obj.number
    }


def ImageCollection_dict_to_class(classname, d):
    # print("{deserializer hook, converting to class: %s}" % d)
    return ImageCollection()


register_dict_to_class("ImageCollection", ImageCollection_dict_to_class)
register_class_to_dict(ImageCollection, ImageCollection_class_to_dict)