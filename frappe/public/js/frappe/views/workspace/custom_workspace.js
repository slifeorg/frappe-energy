frappe.provide("frappe.views");

// Function to check if the current page has a sidebar (Workspace page)
function isWorkspacePage() {
    return document.querySelector(".desk-sidebar") !== null;
}

// Function to update sidebar counts
function updateSidebarCounts() {
    let stats = {};

    frappe.call({
        method: "frappe.utils.job_statistics.get_job_statistics",
        args: {
            user: frappe.session.user, // Pass current user
            roles: frappe.user_roles    // Pass user roles
        },
        callback: function(r) {
            if (r.message) {
                stats = r.message;
            }
        },
        error: function(e) {
            console.error("Error fetching stats:", e);
            stats = {};
        },
        async: false // Ensure synchronous call to update counts immediately
    });

    // Update the sidebar if it exists
    if (document.querySelector(".desk-sidebar")) {
        const sidebarItems = document.querySelectorAll(".desk-sidebar .standard-sidebar-item");
        const stat_mapping = {
            "CF1R": "cf1r_active_job",
            "PERMITS": "permit_active_job",
            "HERS TESTS": "hers_test_active_job",
            "AIR BALANCE": "air_balance_active_job",
            "TITLE 24": "title_24_active_job"
        };

        sidebarItems.forEach(item => {
            const label = item.querySelector(".sidebar-item-label");
            if (!label) return;
            const title = label.textContent.trim().toUpperCase();

            if (stat_mapping[title] && stats[stat_mapping[title]] !== undefined && stats[stat_mapping[title]] > 0) {
                const count = stats[stat_mapping[title]];
                const existingCount = item.querySelector(".sidebar-count");
                if (existingCount) existingCount.remove();
                label.insertAdjacentHTML("afterend", `<span class="sidebar-count">${count}</span>`);
            }
        });

        // Force sidebar redraw
        const sidebar = document.querySelector(".desk-sidebar");
        sidebar.style.display = "none";
        setTimeout(() => {
            sidebar.style.display = "";
        }, 10);
    }
}

// Initialize sidebar on Workspace pages
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(function() {
        if (!isWorkspacePage()) return;

        if (!frappe.views.Workspace || !frappe.views.Workspace.prototype) {
            updateSidebarCounts(); // Proceed with DOM update
            return;
        }

        if (!frappe.views.Workspace.prototype.sidebar_item_container_original) {
            frappe.views.Workspace.prototype.sidebar_item_container_original = frappe.views.Workspace.prototype.sidebar_item_container;
        }

        frappe.views.Workspace.prototype.sidebar_item_container = function(item) {
            let $item = this.sidebar_item_container_original(item);
            const stat_mapping = {
                "CF1R": "cf1r_active_job",
                "PERMITS": "permit_active_job",
                "HERS TESTS": "hers_test_active_job",
                "AIR BALANCE": "air_balance_active_job",
                "TITLE 24": "title_24_active_job"
            };

            if (!this.job_stats) {
                frappe.call({
                    method: "frappe.utils.job_statistics.get_job_statistics",
                    args: {
                        user: frappe.session.user,
                        roles: frappe.user_roles
                    },
                    callback: function(r) {
                        this.job_stats = r.message || {};
                    }.bind(this),
                    error: function(e) {
                        console.error("Error fetching stats:", e);
                        this.job_stats = {};
                    },
                    async: false
                });
            }

            const title = item.title.toUpperCase();
            if (stat_mapping[title] && this.job_stats[stat_mapping[title]] !== undefined && this.job_stats[stat_mapping[title]] > 0) {
                const count = this.job_stats[stat_mapping[title]];
                const $label = $item.find(".sidebar-item-label");
                $label.after(`<span class="sidebar-count">${count}</span>`);
            }

            return $item;
        };

        updateSidebarCounts();
    }, 2000);
});

// Refresh on route change for Workspace pages
frappe.router.on("change", function() {
    if (isWorkspacePage()) {
        updateSidebarCounts();
    }
});
