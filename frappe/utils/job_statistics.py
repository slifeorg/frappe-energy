import frappe

@frappe.whitelist()
def get_job_statistics(user=None, roles=None):
    """
    Fetch job statistics based on user role.
    - Admins see all jobs.
    - Non-admins see only jobs they own.
    """

    # Ensure roles is a list
    if isinstance(roles, str):
        try:
            roles = frappe.parse_json(roles)  # Convert JSON string to list
        except Exception:
            roles = []  # Default to empty list if parsing fails

    # Default excluded statuses
    excluded_statuses = ["COMPLETED", "N/A"]

    # SQL query with placeholders for security
    sql_query = """
        SELECT
            CAST(SUM(CASE WHEN job_status NOT IN ({}) THEN 1 ELSE 0 END) AS UNSIGNED) AS all_active_job,
            CAST(SUM(CASE WHEN air_balance_status NOT IN ({}) AND type = 'AIR BALANCE' THEN 1 ELSE 0 END) AS UNSIGNED) AS air_balance_active_job,
            CAST(SUM(CASE WHEN title24_status NOT IN ({}) AND type = 'TITLE 24'  THEN 1 ELSE 0 END) AS UNSIGNED) AS title_24_active_job,
            CAST(SUM(CASE WHEN hers_status NOT IN ({}) AND (type = 'HERS & PERMITS' OR type = 'HERS TESTS ONLY') THEN 1 ELSE 0 END) AS UNSIGNED) AS hers_test_active_job,
            CAST(SUM(CASE WHEN permit_status NOT IN ({}) AND type = 'PERMIT ONLY' THEN 1 ELSE 0 END) AS UNSIGNED) AS permit_active_job,
            CAST(SUM(CASE WHEN cf1r_status NOT IN ({}) AND type = 'CF1R' THEN 1 ELSE 0 END) AS UNSIGNED) AS cf1r_active_job
        FROM `tabJob`
    """.format(", ".join(["%s"] * len(excluded_statuses)))

    # Determine if the user is an admin
    is_admin = "Admin" in roles

    # Prepare query parameters
    params = excluded_statuses * 6  # Repeat list for each column check
    if not is_admin:
        sql_query += " WHERE owner = %s"
        params.append(user)  # Add owner filter if not admin

    try:
        # Execute query
        result = frappe.db.sql(sql_query, params, as_dict=True)

        # Return result or default values if empty
        return result[0] if result else {key: 0 for key in [
            "all_active_job", "air_balance_active_job", "title_24_active_job",
            "hers_test_active_job", "permit_active_job", "cf1r_active_job"
        ]}
    except Exception as e:
        frappe.log_error(f"Error fetching job statistics: {str(e)}", "Job Statistics Error")
        return {key: 0 for key in [
            "all_active_job", "air_balance_active_job", "title_24_active_job",
            "hers_test_active_job", "permit_active_job", "cf1r_active_job"
        ]}
