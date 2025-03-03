import frappe

@frappe.whitelist()
def get_job_statistics():
    job_stat_doctype = "Job Statistic"

    if not frappe.db.exists("DocType", job_stat_doctype):
        return {
            "cf1r_active_job": 0,
            "permit_active_job": 0,
            "hers_test_active_job": 0,
            "air_balance_active_job": 0,
            "title_24_active_job": 0
        }

    try:
        job_stat = frappe.get_doc(job_stat_doctype)
        return {
            "cf1r_active_job": job_stat.cf1r_active_job or 0,
            "permit_active_job": job_stat.permit_active_job or 0,
            "hers_test_active_job": job_stat.hers_test_active_job or 0,
            "air_balance_active_job": job_stat.air_balance_active_job or 0,
            "title_24_active_job": job_stat.title_24_active_job or 0
        }
    except frappe.DoesNotExistError:
        return {
            "cf1r_active_job": 0,
            "permit_active_job": 0,
            "hers_test_active_job": 0,
            "air_balance_active_job": 0,
            "title_24_active_job": 0
        }