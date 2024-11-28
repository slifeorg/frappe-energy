// Copyright (c) 2022, Frappe Technologies Pvt. Ltd. and Contributors
// MIT License. See LICENSE

frappe.ui.form.LinkedWith = class LinkedWith {
	constructor(opts) {
		$.extend(this, opts);
	}

	show() {
		if (!this.dialog) this.make_dialog();

		$(this.dialog.body).html(
			`<div class="text-muted text-center" style="padding: 30px 0px">
				${__("Loading")}...
			</div>`
		);

		this.dialog.show();
	}

	make_dialog() {
		this.dialog = new frappe.ui.Dialog({
			title: __("Linked With"),
		});

		this.dialog.on_page_show = () => {
			frappe
				.xcall("frappe.desk.form.linked_with.get", {
					doctype: this.frm.doctype,
					docname: this.frm.docname,
				})
				.then((r) => {
					this.frm.__linked_docs = r;
				})
				.then(() => this.make_html());
		};
	}

	make_html() {
		let html = "";
		const linked_docs = this.frm.__linked_docs;
		const linked_doctypes = Object.keys(linked_docs);
	
		if (linked_doctypes.length === 0) {
			html = __("Not Linked to any record");
		} else {
			html = linked_doctypes
				.map((doctype) => {
					const docs = linked_docs[doctype];
					return `
						<div class="list-item-table margin-bottom">
							${this.make_doc_head(doctype)}
							${docs
								.map((doc, index) =>
									this.make_doc_row(doc, doctype, index === docs.length - 1) // Pass a flag for the last row
								)
								.join("")}
						</div>
					`;
				})
				.join("");
		}
	
		$(this.dialog.body).html(html);
	}
	
	make_doc_head(heading) {
		return `
			<header class="level list-row list-row-head text-muted small">
				<div>${__(heading)}</div>
			</header>
		`;
	}
	
	make_doc_row(doc, doctype, is_last_row) {
		const last_row_class = is_last_row ? "custom-last-row" : ""; // Add custom class if it’s the last row
		return `<div class="list-row-container ${last_row_class}">
			<div class="level list-row small">
				<div class="level-left bold">
					<a href="/app/${frappe.router.slug(doctype)}/${doc.name}">${doc.name}</a>
				</div>
			</div>
		</div>`;
	}	
};
