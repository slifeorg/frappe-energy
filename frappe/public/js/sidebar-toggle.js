frappe.router.on("change", function () {
    // Hiding the sidebar
    setTimeout(() => $(".list-sidebar, .form-sidebar").removeClass("show-sidebar"), 200);

    // Waiting for the page to fully load
    const waitForActivePage = setInterval(() => {
        const $activePage = $(".page-container").filter(function () {
            return $(this).css("display") !== "none";
        }).first();

        if ($activePage.length > 0) {
            clearInterval(waitForActivePage);
            // console.log($activePage);
            waitForSidebar($activePage);
        }
    })

    // Skipping the process of waiting after 2s
    setTimeout(() => clearInterval(waitForActivePage), 2000);
});

function waitForSidebar($activePage, attempt = 0) {
    const sidebar = $activePage.find(".list-sidebar, .form-sidebar");
    if (sidebar.length > 0) {
        $(".custom-go-back").remove();

        // Adding a button for opening the sidebar
        if ($(".custom-toggle-sidebar").length === 0) {
            const toggleBtn = $(`<button class="custom-toggle-sidebar"><div class="burger-icon"></div></button>`);
            toggleBtn.on('click', () => $(".list-sidebar, .form-sidebar").toggleClass("show-sidebar"));
            $(".navbar").prepend(toggleBtn);
        }

        // Checking, if sidebar-top already exists
        if (sidebar.find(".sidebar-top").length === 0) {
            const backBtn = $(`<button class="custom-close-sidebar"><div class="arrow-back-icon"></div></button>`);
            backBtn.on("click", () => $(".list-sidebar, .form-sidebar").removeClass("show-sidebar"));

            const sidebarTop = $(`
                <div class="sidebar-top">
                    <a href="/app">
                        <img src="/files/energy-masters-logo.png" alt="App Logo" class="sidebar-top-logo">
                    </a>
                </div>
            `);
            sidebarTop.prepend(backBtn);
            sidebar.prepend(sidebarTop);
        }
    } else if (attempt < 20) {
        // Retrying every 100ms for 2s
        setTimeout(() => waitForSidebar($activePage, attempt + 1), 100);

        if (attempt === 10) {
            addBackButton($activePage);
        }
    } else {
        console.warn("Sidebar not found on this page after waiting.");
    }
}

function addBackButton($activePage) {
    const toggleBtn = $(`<button class="custom-go-back"><div class="arrow-back-icon"></div></button>`);
    toggleBtn.on('click', () => window.history.back());
    $(".navbar").prepend(toggleBtn);   
}
