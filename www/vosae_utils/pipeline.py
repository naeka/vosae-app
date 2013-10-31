# -*- coding:Utf-8 -*-

from PIL import Image


__all__ = (
    'Pipeline',
    'FilePipeline',
    'ImagePipeline'
)


class Pipeline(object):

    """
    Basic Pipeline operations handler  
    Each operation must have its `process_%` handler or will be ignored
    """
    obj = None
    pipeline = []

    def __new__(cls, obj, pipeline):
        instance = super(Pipeline, cls).__new__(cls)
        instance.obj = obj
        instance.pipeline = pipeline
        for line in instance.pipeline:
            for step, action in line.items():
                func = u'process_{0}'.format(step)
                if hasattr(instance, func):
                    instance.obj = getattr(instance, func)(action)
        return instance.obj


class FilePipeline(Pipeline):

    """Pipeline that processes files"""

    def process_image(self, action):
        try:
            original = Image.open(self.obj)
            image = ImagePipeline(original, action)
            self.obj.open('w')
            image.save(self.obj)
            self.obj.close()
            return self.obj
        except:
            raise BufferError("cannot perform image operations")


class ImagePipeline(Pipeline):

    """Pipeline that processes image files"""

    def process_ratio(self, ratio):
        """
        Crop at a given ratio  
        Ratio is [width, height], width and height must be int or float
        """
        ratio = float(ratio[0]) / ratio[1]
        img_width, img_height = self.obj.size
        img_ratio = float(img_width) / img_height

        if img_ratio == ratio:
            return self.obj

        if img_ratio > ratio:
            height = img_height
            width = int(height * ratio)
            offset = int((img_width - width) / 2)
            geometry = (offset, 0, offset + width, height)
        else:
            width = img_width
            height = int(width / ratio)
            offset = int((img_height - height) / 2)
            geometry = (0, offset, width, offset + height)
        return self.obj.crop(geometry)

    def process_crop(self, geometry):
        """
        Crop at a given geometry  
        Geometry is offsets from [left, top, right, bottom]
        """
        return self.obj.crop(geometry)

    def process_fit(self, geometry):
        """
        Fit at a given geometry  
        Geometry is [width, height], width and height are pixels and must be int
        """
        return self.obj.thumbnail(geometry, Image.ANTIALIAS)

    def process_resize(self, data):
        """
        Resize at a given geometry  
        Data must be geometry or dict  
        Geometry is [width, height], width and height are pixels and must be int  
        Dict must contain:
            - geometry: [width, height]
            - constraint: string, one of "DONT_OVERSIZE"
        """
        if isinstance(data, list):
            return self.obj.resize(data)
        if isinstance(data, dict):
            geometry = data.get('geometry')
            constraint = data.get('constraint', None)
            if constraint == "DONT_OVERSIZE" and (self.obj.size[0] < geometry[0] or self.obj.size[1] < geometry[1]):
                return self.process_ratio(geometry)
            else:
                return self.obj.resize(geometry)
