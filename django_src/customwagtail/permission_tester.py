from wagtail.models import PagePermissionTester


class MyPagePermissionTester(PagePermissionTester):
    """
    Custom permission tester for pages that are managed by non Admin users (Businesses and Mentors).
    """

    def can_unpublish(self):
        # Override the method so the new unpublish permission can be set
        if not self.user.is_active:
            return False
        if (not self.page.live) or self.page_is_root:
            return False
        if self.page_locked():
            return False

        return self.user.is_superuser or ("unpublish" in self.permissions)

    def can_publish(self):
        # Override the method so business and mentor users can not publish
        if not self.user.is_active:
            return False
        if self.page_is_root:
            return False
        if self.user.is_business or self.user.is_mentor:
            return False

        return self.user.is_superuser or ("publish" in self.permissions)
