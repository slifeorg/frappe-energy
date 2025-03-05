import frappe

@frappe.whitelist()
def get_job_statistics(user, roles):
    excluded_statuses = ['COMPLETED', 'N/A']
    field_mapping = {
        'job_status': 'all_active_job',
        'air_balance_status': 'air_balance_active_job',
        'title24_status': 'title_24_active_job',
        'hers_status': 'hers_test_active_job',
        'permit_status': 'permit_active_job',
        'cf1r_status': 'cf1r_active_job'
    }

    # Convert roles to a list if it's a string (received from the frontend)
    if isinstance(roles, str):
        roles = frappe.parse_json(roles)

    # Check if the user has the "Admin" role
    is_admin = "Admin" in roles

    # Generate SQL placeholders for excluded statuses
    status_placeholders = ', '.join(['%s'] * len(excluded_statuses))
    owner_condition = "" if is_admin else "AND owner = %s"

    # Construct SQL query to count active jobs based on status
    sql_query = f"""
        SELECT
            CAST(SUM(CASE WHEN job_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS all_active_job,
            CAST(SUM(CASE WHEN air_balance_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS air_balance_active_job,
            CAST(SUM(CASE WHEN title24_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS title_24_active_job,
            CAST(SUM(CASE WHEN hers_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS hers_test_active_job,
            CAST(SUM(CASE WHEN permit_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS permit_active_job,
            CAST(SUM(CASE WHEN cf1r_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS cf1r_active_job
        FROM `tabJob`
        WHERE 1=1 {owner_condition}
    """

    # Prepare values for SQL query
    values = excluded_statuses * len(field_mapping)
    if not is_admin:
        values.append(user)  # Add owner filter if the user is not an admin

    try:
        # Execute SQL query
        result = frappe.db.sql(sql_query, values, as_dict=True)

        # If the query is successful, return the first record
        if result:
            return result[0]
        else:
            raise Exception("Empty SQL result")

    except Exception as e:
        # Log error in Frappe's error logs
        frappe.log_error(f"Error fetching job statistics: {str(e)}", "get_job_statistics")

        # Return default values with 0 in case of an error
        return {key: 0 for key in field_mapping.values()}
