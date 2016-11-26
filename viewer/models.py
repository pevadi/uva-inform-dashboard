from django.db import models

import random

class GroupAssignment(models.Model):
    GROUPS = (('A',"Dashboard"), ('B', "No dashboard"))
    group = models.CharField(max_length=1, choices=GROUPS)
    student = models.CharField(max_length=255)
    datetime = models.DateTimeField(auto_now_add=True)

    @classmethod
    def get_or_assign(cls, student):
        try:
            assignment = cls.objects.filter(student=student).get()
        # Case 1: New user
        except cls.DoesNotExist:
            choices = dict(cls.GROUPS).keys()
            # Case 1a: First half of new pair,
            #          randomly pick A or B for this user.
            if cls.objects.count() % 2 == 0:
                group = random.choice(choices)
            # Case 1b: Second half of new pair,
            #          choose the group that was not previously chosen.
            else:
                try:
                    last_group = cls.objects.order_by('-id')[0].group
                except:
                    last_group = random.choice(choices)
                choices.remove(last_group)
                group = choices[0]
            return cls.objects.create(student=student, group=group)
        # Case 2: Existing user
        else:
            return assignment

    @property
    def has_treatment(self):
        return self.group == 'A'
