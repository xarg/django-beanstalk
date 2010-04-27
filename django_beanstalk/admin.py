from beanstalkc import Connection, SocketError
from datetime import datetime, timedelta

from django.contrib import admin
from django.conf.urls.defaults import url, patterns
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models.options import Options

from models import BeanstalkDaemon

def tubes(obj):
    return "<a href='/tubes/%s'>Browse</a>" % obj.pk
tubes.short_description = 'Browse'

class BeanstalkDaemonAdmin(admin.ModelAdmin):
    """ """

    client = None # beanstalk.Connection
    error = ''

    class Meta:
        verbose_name = "Beanstalk Daemons"

    def get_urls(self):
        urlpatterns = patterns('',
            url(r'^tube/(?P<beanstalk_daemon_pk>\d+)/(?P<name>\w+)$',
                self.admin_site.admin_view(self.tube, cacheable=True), name='tube'),
        )
        return super(BeanstalkDaemonAdmin, self).get_urls() + urlpatterns

    def change_view(self, request, object_id, extra_context=None):
        """ Connect to a beanstalk daemon """

        if extra_context is None:
            extra_context = dict()
        stats = []
        tubes = []

        stats_fields = ['current-connections', 'uptime', 'job-timeouts', 'version',
        'current-jobs-buried','total-jobs', ]

        self.set_client(object_id) #Setting up connection to beanstalk server

        if self.client:
            tubes = self.client.tubes()
            beanstalk_stats = self.client.stats()
            beanstalk_stats['uptime'] = datetime.now() - timedelta(seconds=beanstalk_stats['uptime'])

            # Show only a few stats
            stats = filter(
                lambda pair: pair[0] in stats_fields,
                beanstalk_stats.items()
            )
        extra_context.update(
            error = self.error,
            tubes = tubes,
            stats = stats,
        )
        return super(BeanstalkDaemonAdmin, self).change_view(request, object_id, extra_context)

    def tube(self, request, beanstalk_daemon_pk, name='default'):
        """ View tube stats and list of jobs """

        self.set_client(beanstalk_daemon_pk)
        jobs = []

        if request.method == 'POST':
            pass
        else:
            stats_fields = ['total-jobs', 'current-watching', 'current-using', ]
            jobs_list = [ jl for jl in self.client.peek_ready(), self.client.peek_buried(), self.client.peek_delayed() if jl ]
            for job in jobs_list:
                job_stats = job.stats()
                jobs.append({
                    'id': job.jid,
                    'age': datetime.now() - timedelta(seconds=job_stats['age']),
                    'state': job_stats['state'],
                    'body': job.body,
                })
            opts = Options('', '')
            opts.verbose_name_plural = self.opts.verbose_name
            opts.app_name = 'django_beanstalk'
            return render_to_response('admin/django_beanstalk/beanstalkdaemon/tube.html', {
                'app_name': 'django_beanstalk',
                'opts': opts,
                'jobs': jobs,
                'stats': filter(
                    lambda pair: pair[0] in stats_fields,
                    self.client.stats_tube(name).items()
                ),
                'error': self.error,

            },
            context_instance=RequestContext(request))
    def job(self, request, tube, **kwargs):
        """ Job actions: release, bury.."""
        pass

    def set_client(self, object_id):
        """
        Set up connection to beanstalk server
        object_id: BeanstalkDaemon pk
        """
        try:
            beanstalk_daemon_data = self.model.objects.get(pk=object_id)
            self.client = Connection(
                host=beanstalk_daemon_data.host,
                port=beanstalk_daemon_data.port
            )
        except SocketError, e:
            self.error = e

admin.site.register(BeanstalkDaemon, BeanstalkDaemonAdmin)