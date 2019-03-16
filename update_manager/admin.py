from django.contrib import admin

from update_manager.models import (NeutronApplication, UpdaterList,
                                   VersionControl)

admin.site.site_header = 'Neutron System Administration'


@admin.register(UpdaterList)
class UpdaterListAdminUI(admin.ModelAdmin):
    list_display = ('user', 'get_updaters')

    def get_updaters(self, object):
        print(object.updaters)


@admin.register(NeutronApplication)
class ApplicationsAdminUI(admin.ModelAdmin):
    list_display = ('get_name', 'get_branches', 'get_components')

    def get_readonly_fields(self, request, obj=None):
        if obj:
            return ('name', 'branches', 'components')
        else:
            return ()

    def get_branches(self, object):
        branches = ''
        for branch in object.branches['branches']:
            branches += branch.capitalize()+', '

        return branches[:-2]
    get_branches.short_description = 'Branches'

    def get_components(self, object):
        if not object.components['components']:
            return 'No components registered'
        else:
            components = ''
            for component in object.components['components']:
                components += component+', '

            return components[:-2]
    get_components.short_description = 'Components'

    def get_name(self, object):
        return object.name
    get_name.short_description = 'Application Name'


@admin.register(VersionControl)
class VersionControlAdminUI(admin.ModelAdmin):
    list_display = ('get_app', 'get_versions', 'last_updated')

    # def get_readonly_fields(self, request, obj=None):
    #     if obj:
    #         return ('application')
    #     else:
    #         return ()

    def get_app(self, object):
       return object.application
    get_app.short_description = 'Application'

    def get_versions(self, object):
       return object.versions
    get_versions.short_description = 'Version Information'
