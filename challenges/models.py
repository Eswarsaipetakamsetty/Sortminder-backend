from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    def __str__(self):
        return self.name
    
class Challenges(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    difficulty = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'),
                 ('intermediate', 'Intermediate'),
                 ('advanced', 'Advanced')]
    )
    points = models.IntegerField()
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    input_format = models.TextField(null=True, blank=True)
    output_format = models.TextField(null=True, blank=True)
    constraints = models.TextField(null=True, blank=True)
    sample_input = models.TextField()
    sample_output = models.TextField()
    min_score = models.IntegerField(default=0)
    max_score = models.IntegerField(default=0)
    total_testcases = models.IntegerField(default=0, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

class TestCases(models.Model):
    challenge = models.ForeignKey(Challenges, related_name="testcases", on_delete=models.CASCADE)
    input = models.TextField()
    expected_output = models.TextField()
    is_hidden = models.BooleanField()
    score = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Testcase for {self.challenge.title}"
    