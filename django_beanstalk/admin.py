from beanstalkc import Connection, SocketError
from datetime import datetime, timedelta

from django.contrib import admin
from django.conf.urls.defaults import url, patterns
from django.http import HttpResponseRedirect, Http404
from django.shortcuts import render_to_response
from django.template import RequestContext
from django.db.models.options import Options

from models import BeanstalkDaemon
from forms import BeanstalkJobForm

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
            url(r'^job/(?P<beanstalk_daemon_pk>\d+)/(?P<tube>\w+)/(?P<job_id>\d+)/(?P<action>\w+)$',
                self.admin_site.admin_view(self.job), name='job'),
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

        self._set_client(object_id) #Setting up connection to beanstalk server

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
        self._set_client(beanstalk_daemon_pk)

        if request.method == 'POST': # Add a new job to tube
            form = BeanstalkJobForm(request.POST)
            if form.is_valid():
                self.client.use(name)
                self.client.put(str(form.cleaned_data.get('body', None)))
        else:
            form = BeanstalkJobForm()

        self.client.watch(name) # Start watching this tube

        jobs = []
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
            'form': form,
            'app_label': 'django_beanstalk',
            'beanstalk_daemon_pk': beanstalk_daemon_pk,
            'original': self.beanstalk_daemon_str,
            'name': name,
            'opts': opts,
            'jobs': jobs,
            'stats': filter(
                lambda pair: pair[0] in stats_fields,
                self.client.stats_tube(name).items()
            ),
            'error': self.error,
        },
        context_instance=RequestContext(request))

    def job(self, request, beanstalk_daemon_pk, tube, job_id, action):
        """ Job actions: release, bury.."""
        self._set_client(beanstalk_daemon_pk)
        self.client.use(tube)
        if action == 'delete':
            self.client.delete(int(job_id))
        elif action == 'kick':
            self.client.kick(int(job_id))

        return HttpResponseRedirect(request.META.get('HTTP_REFERER', '/admin/django_beanstalk/'))

    def _set_client(self, object_id):
        """
        Set up connection to beanstalk server
        object_id: BeanstalkDaemon pk
        """
        try:
            beanstalk_daemon_data = self.model.objects.get(pk=object_id)
            self.beanstalk_daemon_str = str(beanstalk_daemon_data)
            self.client = Connection(
                host=beanstalk_daemon_data.host,
                port=beanstalk_daemon_data.port
            )
        except SocketError, e:
            self.error = e

admin.site.register(BeanstalkDaemon, BeanstalkDaemonAdmin)
