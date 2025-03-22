from django.db import models


class NetworksDB(models.Model):
    sys_name = models.CharField(max_length=32)
    int_name = models.CharField(max_length=32)
    int_ipaddr = models.CharField(max_length=32)
    

class PhysicalDB(models.Model):
    obj_code = models.CharField(max_length=5)
    obj_name = models.CharField(max_length=128)
    obj_addr = models.CharField(max_length=256)
