import time
import os.path
import peewee as pw



class Box(pw.Model):
    quest = pw.TextField()
    answer = pw.TextField()
    rep_group = pw.IntegerField(default=0)  # 0 for none and 1 for all
    user_id = pw.IntegerField(default=0)
    allow_private = pw.BooleanField(default=False)
    creator = pw.IntegerField()
    get_time = pw.TimestampField()

    class Meta:
        database = db
        primary_key = pw.CompositeKey('quest', 'rep_group', 'rep_member')