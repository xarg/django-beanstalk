from django.db import models

class BeanstalkDaemon(models.Model):
    """ Used to store the connection info to beanstalk daemons """
    host = models.CharField(max_length=200, default="localhost")
    port = models.IntegerField(default=11300)

    def __unicode__(self):
        return "%s:%s" % (self.host, self.port)
