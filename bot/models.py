from django.db import models


class User(models.Model):
    id = models.AutoField(primary_key=True)
    user_id = models.IntegerField()
    inviter_id = models.IntegerField(default=0, auto_created=True, null=True)
    registration_date = models.DateTimeField(auto_now_add=True, null=True)
    money = models.IntegerField(null=True, default=0)
    invited_users = models.TextField(null=True)
    has_sub = models.BooleanField(default=False)
