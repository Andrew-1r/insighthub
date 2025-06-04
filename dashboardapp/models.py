# models.py
from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.pk)

# to create a new user
# user = User.objects.create_user(username="x", email="y", password="z")
# profile = UserProfile.objects.create(user=user)

class UserCSV(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    csv_title = models.CharField(max_length=255)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    csv_file = models.FileField(upload_to='csv_files/')

    def __str__(self):
        return str(self.pk)

class CSVHeading(models.Model):
    csv = models.ForeignKey(UserCSV, on_delete=models.CASCADE)
    heading_name = models.CharField(max_length=255)

    def __str__(self):
        return str(self.pk)

class CSVValue(models.Model):
    csv = models.ForeignKey(UserCSV, on_delete=models.CASCADE)
    heading = models.ForeignKey(CSVHeading, on_delete=models.CASCADE)
    row_index = models.IntegerField()
    value = models.TextField()

    def __str__(self):
        return str(self.pk)

# could only allow editing if dashboard.userid = user.userid
class Dashboard(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    is_public = models.BooleanField(default=False)
    qr_code_image = models.ImageField(upload_to='qrcodes/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    layout_json = models.JSONField(blank=True, null=True)

    def __str__(self):
        return str(self.pk)
