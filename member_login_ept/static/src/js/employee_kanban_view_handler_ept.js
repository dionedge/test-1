
odoo.define('member_login_ept.employee_kanban_view_handler_ept', function(require) {
"use strict";

var KanbanRecord = require('web.KanbanRecord');

KanbanRecord.include({
    //--------------------------------------------------------------------------
    // Private
    //--------------------------------------------------------------------------

    /**
     * @override
     * @private
     */
    _openRecord: function () {
        if (this.modelName === 'res.partner' && this.$el.parents('.o_hr_employee_attendance_kanban_member').length) {
                                            // needed to diffentiate : check in/out kanban view of employees <-> standard employee kanban view
            var action = {
                type: 'ir.actions.client',
                name: 'Confirm',
                tag: 'hr_attendance_kiosk_confirm_ept',
                partner_id: this.record.id.raw_value,
                partner_name: this.record.name.raw_value,
                partner_state: this.record.attendance_state.raw_value
            };
            this.do_action(action);
        } else {
            this._super.apply(this, arguments);
        }
    }
});

});
