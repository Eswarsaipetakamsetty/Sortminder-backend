from rest_framework import serializers
from .models import Challenges, TestCases, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name']

class TestCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestCases
        fields = [
            'id',
            'input',
            'expected_output',
            'is_hidden',
            'score',
            'created_at'
        ]

class ChallengeSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only = True)
    testcases = TestCaseSerializer(many=True, read_only=True)
    class Meta:
            model = Challenges
            fields = [
                'id',
                'title',
                'description',
                'difficulty',
                'points',
                'category',
                'input_format',
                'output_format',
                'constraints',
                'sample_input',
                'sample_output',
                'min_score',
                'max_score',
                'total_testcases',
                'created_at',
                'testcases',
            ]