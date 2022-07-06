from django.core.files.storage import get_storage_class
from django.db import models
from PIL import Image
import os
import json

from django.urls import reverse


class License(models.Model):
    name = models.CharField(max_length=255)
    url = models.URLField()

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


def thumbnail_path(instance, filename):
    return f'thumbnails/{instance.id}.jpg'


def file_storage_path(instance, filename):
    return f'uploads/{instance.id}/data.zip'


class OverwriteStorage(get_storage_class()):
    def _save(self, name, content):
        self.delete(name)
        return super(OverwriteStorage, self)._save(name, content)

    def get_available_name(self, name, max_length=None):
        return name


class Item(models.Model):
    id = models.SlugField(max_length=100, primary_key=True)
    name = models.CharField(max_length=255)
    description = models.TextField()
    license = models.ForeignKey(License, on_delete=models.CASCADE)
    license_custom = models.TextField(blank=True)
    copyright = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    tag = models.ManyToManyField(Tag)
    thumbnail = models.ImageField(upload_to=thumbnail_path, default='thumbnails/default.png', storage=OverwriteStorage())

    PIPELINE = 'pipeline'
    DATA = 'data'
    MODEL = 'model'
    ITEM_TYPES = [
        (PIPELINE, 'Pipeline'),
        (DATA, 'Data'),
        (MODEL, 'Model'),
    ]
    type = models.CharField(choices=ITEM_TYPES, max_length=16, default=PIPELINE)

    min_fast_version = models.CharField(max_length=10, blank=True) # Should be a FAST version number
    max_fast_version = models.CharField(max_length=10, blank=True) # Should be a FAST version number
    date = models.DateField()
    needs = models.ManyToManyField('self', symmetrical=False, blank=True, related_name='needed_by') # Which items this item needs to function. Typically, just for pipelines..
    replaces = models.OneToOneField('self', blank=True, null=True, on_delete=models.CASCADE) # Which item this item replaces, if any
    download_counter = models.PositiveBigIntegerField(default=0)

    # File can either be stored locally or at a specific URL, or a pipeline text stored in DB
    local_file = models.FileField(upload_to=file_storage_path, blank=True, storage=OverwriteStorage())
    external_url = models.URLField(blank=True)
    pipeline_text = models.TextField(blank=True)

    def __str__(self):
        return f'{self.id}: {self.name}'

    def save(self, **kwargs):
        super().save(kwargs)
        if not self.thumbnail.path.endswith('/default.png'):
            image = Image.open(self.thumbnail.path)
            image.thumbnail((256, 256))
            image = image.convert('RGB')
            image.save(self.thumbnail.path, format='JPEG', quality=90)

    def toJSON(self, request):
        needs = []
        for item in self.needs.all():
            needs.append(item.toJSON(request))
        data = {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'license_name': self.license.name,
            'license_url': self.license.url,
            'copyright': self.copyright,
            'author': self.author,
            'downloads': self.download_counter,
            'thumbnail_url': request.build_absolute_uri(self.thumbnail.url),
            'download_url': request.build_absolute_uri(reverse('download', kwargs={'item_id': self.id})),
            'type': self.type,
            'needs': needs,
        }

        return data

    def all_authors(self):
        result = set()
        list = [self]
        while len(list) > 0:
            item = list.pop()
            result.add(item.author)

            for item2 in item.needs.all():
                list.append(item2)
        return result

    def all_copyrights(self):
        result = set()
        list = [self]
        while len(list) > 0:
            item = list.pop()
            if item.type != Item.PIPELINE:
                result.add(item.copyright)

            for item2 in item.needs.all():
                list.append(item2)
        return result

    def all_licences(self):
        result = {}
        list = [self]
        while len(list) > 0:
            item = list.pop()
            if item.type != Item.PIPELINE:
                result[item.license.name] = item.license.url

            for item2 in item.needs.all():
                list.append(item2)
        return result

