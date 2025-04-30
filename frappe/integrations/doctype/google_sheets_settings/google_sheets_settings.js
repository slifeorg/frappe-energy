// Copyright (c) 2025, Frappe Technologies and contributors
// For license information, please see license.txt

frappe.ui.form.on("Google Sheets Settings", {
    refresh: function(frm) {
        if (!frm.doc.__islocal) {
            frm.add_custom_button(__("Allow Google Sheets Access"), function() {
                frappe.call({
                    method: "frappe.integrations.doctype.google_sheets_settings.google_sheets_settings.authorize_access",
                    args: {
                        reauthorize: frm.doc.authorization_code ? 1 : 0,
                    },
                    callback: function (r) {
                        if (!r.exc) {
                            frm.save();
                            window.open(r.message.url);
                        }
                    },
                });
            });
        }
    }
});