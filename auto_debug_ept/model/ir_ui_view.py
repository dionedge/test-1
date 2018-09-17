from odoo import api, fields,tools, _
#from odoo.addons.models import BaseModel
from odoo import models

def user_has_groups_ept(self, groups):
    """Return true if the user is member of at least one of the groups in
    ``groups``, and is not a member of any of the groups in ``groups``
    preceded by ``!``. Typically used to resolve ``groups`` attribute in
    view and model definitions.

    :param str groups: comma-separated list of fully-qualified group
        external IDs, e.g., ``base.group_user,base.group_system``,
        optionally preceded by ``!``
    :return: True if the current user is a member of one of the given groups
        not preceded by ``!`` and is not member of any of the groups
        preceded by ``!``
    """
    from odoo.http import request
    user = self.env.user

    has_groups = []
    not_has_groups = []
    for group_ext_id in groups.split(','):
        group_ext_id = group_ext_id.strip()
        if group_ext_id[0] == '!':
            not_has_groups.append(group_ext_id[1:])
        else:
            has_groups.append(group_ext_id)

    for group_ext_id in not_has_groups:
        if group_ext_id == 'base.group_no_one':
            # check: the group_no_one is effective in debug mode only
            if user.has_group(group_ext_id) and request:
                return False
        else:
            if user.has_group(group_ext_id):
                return False

    for group_ext_id in has_groups:
        if group_ext_id == 'base.group_no_one':
            # check: the group_no_one is effective in debug mode only
            if user.has_group(group_ext_id) and request:
                return True
        else:
            if user.has_group(group_ext_id):
                return True

    return not has_groups

models.BaseModel.user_has_groups = user_has_groups_ept
