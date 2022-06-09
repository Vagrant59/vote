from bpmappers import RawField, DelegateField
from bpmappers.djangomodel import ModelMapper

from polls.models import Subject, Teacher


class SubjectSerializer(ModelMapper):
    """学科映射器"""
    isHot = RawField('is_hot')

    class Meta:
        model = Subject
        exclude = ('is_hot', )


class SubjectSimpleSerializer(ModelMapper):
    """学科简单映射器"""

    class Meta:
        model = Subject
        fields = ('no', 'name')


class TeacherSerializer(ModelMapper):
    """老师映射器"""
    goodCount = RawField('good_count')
    badCount = RawField('bad_count')

    class Meta:
        model = Teacher
        exclude = ('subject', )
