from pysmvt import appimportauto, settings
import actions
import difflib

appimportauto('base', ['ProtectedPageView'])

class AuditDiffBase(ProtectedPageView):
    def prep(self):
        self.extend_from = settings.template.default
        self.template_name = 'audit_diff'

    def default(self, rev1, rev2=None):
        ar = actions.audit_record_get(rev1)
        prev_ar = actions.audit_record_get(rev2) if rev2 else actions.get_previous_audit_record(rev1)

        diff_text = difflib.unified_diff(prev_ar.audit_text.splitlines(True), ar.audit_text.splitlines(True), prev_ar.identifier, ar.identifier, prev_ar.createdts, ar.createdts)
        self.assign('diff_text', '<br/>'.join([d for d in diff_text]))
        self.assign('extend_from', self.extend_from)
        