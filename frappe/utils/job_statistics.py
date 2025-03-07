import frappe

@frappe.whitelist()
def get_job_statistics(user=None, roles=None):
    """
    Fetch job statistics based on user role. Admins see all jobs, others see only jobs they own.
    """

    # Ensure roles is a list
    roles = roles or []

    # Default excluded statuses
    excluded_statuses = ("COMPLETED", "N/A")

    # Base query
    sql_query = """
        SELECT
            CAST(SUM(CASE WHEN job_status NOT IN {statuses} THEN 1 ELSE 0 END) AS UNSIGNED) AS all_active_job,
            CAST(SUM(CASE WHEN air_balance_status NOT IN {statuses} AND type = 'AIR BALANCE' THEN 1 ELSE 0 END) AS UNSIGNED) AS air_balance_active_job,
            CAST(SUM(CASE WHEN title24_status NOT IN {statuses} AND type = 'TITLE 24'  THEN 1 ELSE 0 END) AS UNSIGNED) AS title_24_active_job,
            CAST(SUM(CASE WHEN hers_status NOT IN {statuses} AND (type = 'HERS & PERMITS' OR type = 'HERS TESTS ONLY') THEN 1 ELSE 0 END) AS UNSIGNED) AS hers_test_active_job,
            CAST(SUM(CASE WHEN permit_status NOT IN {statuses} AND type = 'PERMIT ONLY' THEN 1 ELSE 0 END) AS UNSIGNED) AS permit_active_job,
            CAST(SUM(CASE WHEN cf1r_status NOT IN {statuses} AND type = 'CF1R' THEN 1 ELSE 0 END) AS UNSIGNED) AS cf1r_active_job
        FROM `tabJob`
    """.format(statuses=excluded_statuses)

    # If the user is NOT an admin, filter jobs by owner
    if "Admin" not in roles:
        sql_query += " WHERE owner = %s"
        params = (user,)
    else:
        params = ()

    try:
        # Execute query
        result = frappe.db.sql(sql_query, params, as_dict=True)

        # Return result or default values if empty
        return result[0] if result else {
            "all_active_job": 0,
            "air_balance_active_job": 0,
            "title_24_active_job": 0,
            "hers_test_active_job": 0,
            "permit_active_job": 0,
            "cf1r_active_job": 0
        }
    except Exception as e:
        frappe.log_error(f"Error fetching job statistics: {str(e)}", "Job Statistics Error")
        return {
            "all_active_job": 0,
            "air_balance_active_job": 0,
            "title_24_active_job": 0,
            "hers_test_active_job": 0,
            "permit_active_job": 0,
            "cf1r_active_job": 0
        }
