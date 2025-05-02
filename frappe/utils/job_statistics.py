import frappe
import json

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

    # Child statuses per parent (excluding COMPLETED and N/A from counts)
    child_statuses = {
        'CF1R': ['NEW', 'PENDING', 'NEEDS ATTENTION'],
        'TITLE 24': ['NEW', 'NEEDS ATTENTION', 'SCHEDULED', 'RESCHEDULED', 'FAILED'],
        'AIR BALANCE': ['NEW', 'PENDING', 'NEEDS ATTENTION', 'SCHEDULED', 'RESCHEDULED', 'FAILED'],
        'HERS TESTS': ['NEW', 'PENDING', 'HERS ONLY', 'NEEDS ATTENTION', 'SCHEDULED', 'RESCHEDULED', 'FAILED'],
        'PERMITS': ['NEW', 'PENDING', 'NEEDS ATTENTION', 'SCHEDULED']
    }

    # Convert roles to a list if it's a string
    if isinstance(roles, str):
        roles = json.loads(roles)

    # Check if the user has the "Admin" role
    is_admin = "Admin" in roles

    # Generate SQL placeholders for excluded statuses
    status_placeholders = ', '.join(['%s'] * len(excluded_statuses))
    owner_condition = "" if is_admin else "AND owner = %s"

    # Construct SQL query with parent and child counts
    sql_query = f"""
        SELECT
            -- Parent-level counts
            CAST(SUM(CASE WHEN job_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS all_active_job,
            CAST(SUM(CASE WHEN air_balance_status NOT IN ({status_placeholders}) AND type = 'AIR BALANCE' THEN 1 ELSE 0 END) AS UNSIGNED) AS air_balance_active_job,
            CAST(SUM(CASE WHEN title24_status NOT IN ({status_placeholders}) AND type = 'TITLE 24' THEN 1 ELSE 0 END) AS UNSIGNED) AS title_24_active_job,
            CAST(SUM(CASE WHEN hers_status NOT IN ({status_placeholders}) AND (type = 'HERS & PERMITS' OR type = 'HERS TESTS ONLY') THEN 1 ELSE 0 END) AS UNSIGNED) AS hers_test_active_job,
            CAST(SUM(CASE WHEN permit_status NOT IN ({status_placeholders}) AND (type = 'HERS & PERMITS' OR type = 'PERMIT ONLY') THEN 1 ELSE 0 END) AS UNSIGNED) AS permit_active_job,
            CAST(SUM(CASE WHEN cf1r_status NOT IN ({status_placeholders}) AND type = 'CF1R' THEN 1 ELSE 0 END) AS UNSIGNED) AS cf1r_active_job,
            -- Child-level counts
            {', '.join([
                f"CAST(SUM(CASE WHEN cf1r_status = '{status}' AND type = 'CF1R' AND cf1r_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS cf1r_{status.lower().replace(' ', '_')}_job"
                for status in child_statuses['CF1R']
            ])},
            {', '.join([
                f"CAST(SUM(CASE WHEN title24_status = '{status}' AND type = 'TITLE 24' AND title24_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS title_24_{status.lower().replace(' ', '_')}_job"
                for status in child_statuses['TITLE 24']
            ])},
            {', '.join([
                f"CAST(SUM(CASE WHEN air_balance_status = '{status}' AND type = 'AIR BALANCE' AND air_balance_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS air_balance_{status.lower().replace(' ', '_')}_job"
                for status in child_statuses['AIR BALANCE']
            ])},
            {', '.join([
                f"CAST(SUM(CASE WHEN hers_status = '{status}' AND (type = 'HERS & PERMITS' OR type = 'HERS TESTS ONLY') AND hers_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS hers_test_{status.lower().replace(' ', '_')}_job"
                for status in child_statuses['HERS TESTS']
            ])},
            {', '.join([
                f"CAST(SUM(CASE WHEN permit_status = '{status}' AND (type = 'HERS & PERMITS' OR type = 'PERMIT ONLY') AND permit_status NOT IN ({status_placeholders}) THEN 1 ELSE 0 END) AS UNSIGNED) AS permit_{status.lower().replace(' ', '_')}_job"
                for status in child_statuses['PERMITS']
            ])}
        FROM `tabJob`
        WHERE 1=1 {owner_condition}
    """

    # Prepare values for SQL query
    values = excluded_statuses * len(field_mapping) + excluded_statuses * (len(child_statuses['CF1R']) + len(child_statuses['TITLE 24']) + len(child_statuses['AIR BALANCE']) + len(child_statuses['HERS TESTS']) + len(child_statuses['PERMITS']))
    if not is_admin:
        values.append(user)

    try:
        result = frappe.db.sql(sql_query, values, as_dict=True)
        if result:
            return result[0]
        else:
            raise Exception("Empty SQL result")
    except Exception as e:
        frappe.log_error(f"Error fetching job statistics: {str(e)}", "get_job_statistics")
        # Return defaults with 0 for all fields
        defaults = {key: 0 for key in field_mapping.values()}
        for parent, statuses in child_statuses.items():
            parent_key = parent.lower().replace(' ', '_')
            for status in statuses:
                defaults[f"{parent_key}_{status.lower().replace(' ', '_')}_job"] = 0
        return defaults