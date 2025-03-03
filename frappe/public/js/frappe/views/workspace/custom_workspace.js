frappe.provide("frappe.views");

//console.log("Custom Workspace script loaded on:", window.location.pathname);

// Function to check if current page has a sidebar (Workspace page)
function isWorkspacePage() {
    const hasSidebar = document.querySelector(".desk-sidebar") !== null;

    // console.log("Checking if Workspace page:");
    // console.log(" - Path:", window.location.pathname);
    // console.log(" - Has sidebar:", hasSidebar);
    // console.log(" - frappe.views.Workspace:", !!frappe.views.Workspace);
    // console.log(" - frappe._workspace:", !!frappe._workspace);

    return hasSidebar;
}

// Function to update sidebar counts
function updateSidebarCounts() {
    // console.log("4: Updating sidebar with latest counts");
    let stats;
    frappe.call({
        method: "frappe.utils.job_statistics.get_job_statistics",
        async: false,
        callback: function(r) {
            // console.log("Stats fetched:", r.message);
            stats = r.message || {};
        },
        error: function(e) {
            console.error("Error fetching stats:", e);
            stats = {};
        }
    });

    // Update DOM directly if sidebar exists
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
                // console.log("Adding count for", title, ":", count);
                // Remove existing count span if any
                const existingCount = item.querySelector(".sidebar-count");
                if (existingCount) existingCount.remove();
                label.insertAdjacentHTML("afterend", `<span class="sidebar-count">${count}</span>`);
            }
        });

        // Force redraw
        // console.log("Forcing sidebar redraw");
        const sidebar = document.querySelector(".desk-sidebar");
        sidebar.style.display = "none";
        setTimeout(() => {
            sidebar.style.display = "";
        }, 10);
    } else {
        console.log("No sidebar found to update");
    }
}

// Initialize sidebar on Workspace pages
document.addEventListener("DOMContentLoaded", function() {
    // console.log("DOMContentLoaded fired");
    setTimeout(function() {
        // console.log("Executing after 2-second delay");

        if (!isWorkspacePage()) {
            console.log("No sidebar present - Skipping execution");
            return;
        }

        // console.log("Sidebar detected - Proceeding");

        if (!frappe.views.Workspace || !frappe.views.Workspace.prototype) {
            console.log("1: Workspace class not ready - Skipping");
            updateSidebarCounts(); // Proceed with DOM update anyway
            return;
        }
        console.log("1: Workspace class loaded");

        if (!frappe.views.Workspace.prototype.sidebar_item_container_original) {
            console.log("2: Storing original sidebar_item_container method");
            frappe.views.Workspace.prototype.sidebar_item_container_original = frappe.views.Workspace.prototype.sidebar_item_container;
        } else {
            console.log("2: Original method already stored");
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
                    async: false,
                    callback: function(r) {
                        // console.log("Stats fetched (inside override):", r.message);
                        this.job_stats = r.message || {};
                    }.bind(this),
                    error: function(e) {
                        console.error("Error fetching stats (inside override):", e);
                        this.job_stats = {};
                    }
                });
            }

            const title = item.title.toUpperCase();
            if (stat_mapping[title] && this.job_stats[stat_mapping[title]] !== undefined && this.job_stats[stat_mapping[title]] > 0) {
                const count = this.job_stats[stat_mapping[title]];
                const $label = $item.find(".sidebar-item-label");
                // console.log("Adding count for", title, ":", count);
                $label.after(`<span class="sidebar-count">${count}</span>`);
            }

            return $item;
        };

        updateSidebarCounts();
    }, 2000); // 2-second delay
});

// Refresh on route change for Workspace pages
frappe.router.on("change", function() {
    // console.log("Route change detected, new path:", window.location.pathname);
    if (isWorkspacePage()) {
        // console.log("Sidebar present after route change - Refreshing sidebar counts");
        updateSidebarCounts();
    }
    // else {
    //     console.log("No sidebar present after route change - Skipping");
    // }
});