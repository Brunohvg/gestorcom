from django.db import models
from django.contrib.auth.models import User

class Profile(models.Model):
    user = models.OneToOneField(User, related_name="profile", on_delete=models.CASCADE)
    nome = models.CharField(max_length=125)
    whatsapp = models.CharField(max_length=15)
    
    def __str__(self) -> str:
        return self.nome