from django.urls import include, path, re_path, reverse
from django.conf.urls.static import static
from django.conf import settings
from django.http import HttpResponseRedirect
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.contrib.sitemaps import views as sitemaps_views, Sitemap
from django.utils.translation import pgettext
from django.contrib import admin
from django.template.response import TemplateResponse

from rest_framework.schemas import get_schema_view

from froide.account.api_views import ProfileView
from froide.foirequest.api_views import (FoiRequestViewSet, FoiMessageViewSet,
    FoiAttachmentViewSet)
from froide.publicbody.api_views import (ClassificationViewSet,
    CategoryViewSet, PublicBodyViewSet, JurisdictionViewSet, FoiLawViewSet)
from froide.georegion.api_views import GeoRegionViewSet
from froide.foirequestfollower.api_views import FoiRequestFollowerViewSet
from froide.campaign.api_views import CampaignViewSet
from froide.upload.api_views import UploadViewSet
from froide.problem.api_views import ProblemReportViewSet
from froide.document.api_views import (
    PageViewSet, DocumentViewSet, DocumentCollectionViewSet,
    PageAnnotationViewSet
)
from froide.document.urls import document_media_urlpatterns

from froide.publicbody.views import (PublicBodySitemap, FoiLawSitemap,
                                     JurisdictionSitemap, show_publicbody,
                                     publicbody_shortlink)
from froide.foirequest.views import FoiRequestSitemap, index, dashboard


from froide.helper import api_router


def handler500(request):
    """
    500 error handler which includes ``request`` in the context.
    """

    from django.shortcuts import render
    return render(request, '500.html', {'request': request}, status=500)


api_router.register(r'request', FoiRequestViewSet, basename='request')
api_router.register(r'message', FoiMessageViewSet, basename='message')
api_router.register(r'attachment', FoiAttachmentViewSet,
                    basename='attachment')
api_router.register(r'publicbody', PublicBodyViewSet, basename='publicbody')
api_router.register(r'category', CategoryViewSet, basename='category')
api_router.register(r'classification', ClassificationViewSet,
                    basename='classification')
api_router.register(r'jurisdiction', JurisdictionViewSet,
                    basename='jurisdiction')
api_router.register(r'law', FoiLawViewSet, basename='law')
api_router.register(r'georegion', GeoRegionViewSet, basename='georegion')
api_router.register(r'following', FoiRequestFollowerViewSet, basename='following')
api_router.register(r'campaign', CampaignViewSet, basename='campaign')
api_router.register(r'upload', UploadViewSet, basename='upload')
api_router.register(r'problemreport', ProblemReportViewSet, basename='problemreport')
api_router.register(r'document', DocumentViewSet, basename='document')
api_router.register(r'documentcollection',
    DocumentCollectionViewSet, basename='documentcollection')
api_router.register(r'page', PageViewSet, basename='page')
api_router.register(r'pageannotation', PageAnnotationViewSet,
    basename='pageannotation')


class StaticViewSitemap(Sitemap):
    priority = 1.0
    changefreq = 'daily'

    def items(self):
        return ['foirequest-list']

    def location(self, item):
        return reverse(item)


sitemaps = {
    'publicbody': PublicBodySitemap,
    'foilaw': FoiLawSitemap,
    'jurisdiction': JurisdictionSitemap,
    'foirequest': FoiRequestSitemap,
    'content': StaticViewSitemap,
}


PROTOCOL = settings.SITE_URL.split(':')[0]

for klass in sitemaps.values():
    klass.protocol = PROTOCOL

sitemap_urlpatterns = [
    path('sitemap.xml', sitemaps_views.index,
        {'sitemaps': sitemaps, 'sitemap_url_name': 'sitemaps'}),
    path('sitemap-<str:section>.xml', sitemaps_views.sitemap,
        {'sitemaps': sitemaps}, name='sitemaps')
]

froide_urlpatterns = []

SECRET_URLS = getattr(settings, "SECRET_URLS", {})

if settings.FROIDE_CONFIG.get('api_activated', True):
    schema_view = get_schema_view(title='{name} API'.format(
                                  name=settings.SITE_NAME))
    froide_urlpatterns += [
        path('api/v1/user/', ProfileView.as_view(), name='api-user-profile'),
        path('api/v1/', include((api_router.urls, 'api'))),
        path('api/v1/schema/', schema_view),
    ]


froide_urlpatterns += [
    # Translators: URL part
    path('', include('froide.foirequest.urls')),
]

if len(settings.LANGUAGES) > 1:
    froide_urlpatterns += [
        path('i18n/', include('django.conf.urls.i18n'))
    ]

account = pgettext('url part', 'account')
documents = pgettext('url part', 'documents')
teams = pgettext('url part', 'teams')

froide_urlpatterns += [
    # Translators: follow request URL
    path('%s/' % pgettext('url part', 'follow'), include('froide.foirequestfollower.urls')),

    re_path(r"^%s/(?P<obj_id>\d+)/?$" % pgettext('url part', 'b'),
        publicbody_shortlink, name="publicbody-publicbody_shortlink"),
    # Translators: URL part
    path('%s/<slug:slug>/' % pgettext('url part', 'entity'), show_publicbody,
            name="publicbody-show"),
    path('%s/' % pgettext('url part', 'entity'),
        lambda request: HttpResponseRedirect(reverse('publicbody-list'))),
    # Translators: URL part
    path('%s/' % pgettext('url part', 'entities'), include('froide.publicbody.urls')),
    # Translators: URL part
    path('%s/' % pgettext('url part', 'law'), include('froide.publicbody.law_urls')),
    path('%s/' % documents, include('froide.document.urls')),
    path('%s/%s/' % (account, teams), include('froide.team.urls')),
    path('%s/' % account, include('froide.account.urls')),
    path('', include('froide.account.export_urls')),
    path('%s/access-token/' % account, include('froide.accesstoken.urls')),
    # Translators: URL part
    path('%s/' % pgettext('url part', 'profile'), include('froide.account.profile_urls')),
    path('comments/', include('django_comments.urls')),
    path('problem/', include('froide.problem.urls')),
    path('moderation/', include('froide.problem.moderation_urls')),
    path(pgettext('url part', 'letter/'), include('froide.letter.urls')),
    path('guide/', include('froide.guide.urls')),
    path('500/', lambda request: TemplateResponse(request, '500.html'))
]

froide_urlpatterns += document_media_urlpatterns

admin_urls = [
        path('%s/' % SECRET_URLS.get('admin', 'admin'), admin.site.urls)
]

if SECRET_URLS.get('postmark_inbound'):
    from froide.foirequest.views import postmark_inbound

    froide_urlpatterns += [
        path('postmark/%s/' % SECRET_URLS['postmark_inbound'],
            postmark_inbound, name="foirequest-postmark_inbound")
    ]

if SECRET_URLS.get('postmark_bounce'):
    from froide.foirequest.views import postmark_bounce

    froide_urlpatterns += [
        path('postmark/%s/' % SECRET_URLS['postmark_bounce'],
            postmark_bounce, name="foirequest-postmark_bounce")
    ]


if settings.DEBUG:
    froide_urlpatterns += staticfiles_urlpatterns()
    froide_urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )

if settings.DEBUG:
    try:
        import debug_toolbar
        froide_urlpatterns = [
            path('__debug__/', include(debug_toolbar.urls)),
        ] + froide_urlpatterns
    except ImportError:
        pass


# Translators: URL part
jurisdiction_part = pgettext('url part', 'jurisdiction')

jurisdiction_urls = [
    path('%s/<slug:slug>/' % jurisdiction_part,
        include('froide.publicbody.jurisdiction_urls'))
]

urlpatterns = froide_urlpatterns + [
    path('', index, name='index'),
    path('dashboard/', dashboard, name='dashboard'),
] + sitemap_urlpatterns + jurisdiction_urls + admin_urls
