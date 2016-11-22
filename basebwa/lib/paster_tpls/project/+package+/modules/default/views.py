from blazeweb import appimportauto
appimportauto('base', ['PublicPageView'])


class Index(PublicPageView):  # noqa
    def default(self):
        pass
