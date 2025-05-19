frappe.router.on("change", function () {
    // Ховаємо Sidebar
    setTimeout(() => $(".list-sidebar").removeClass("show-sidebar"), 200);

    // Отримуємо активну сторінку
    const $activePage = $(".page-container").filter(function () {
        return $(this).css("display") !== "none";
    }).first();

    // Додаємо кнопку відкриття в navbar (один раз)
    if ($(".custom-toggle-sidebar").length === 0) {
        const toggleBtn = $(`<button class="custom-toggle-sidebar"><div class="burger-icon"></div></button>`);
        toggleBtn.on('click', () => $(".list-sidebar").toggleClass("show-sidebar"));
        $(".navbar").prepend(toggleBtn);
    }

    // Очікуємо появу .list-sidebar всередині активної сторінки
    waitForSidebar($activePage);
});

function waitForSidebar($activePage, attempt = 0) {
    const sidebar = $activePage.find(".list-sidebar");
    if (sidebar.length > 0) {
        // Перевірка, чи вже є елемент .sidebar-top
        if (sidebar.find(".sidebar-top").length === 0) {
            const backBtn = $(`<button class="custom-close-sidebar"><div class="arrow-back-icon"></div></button>`);
            backBtn.on("click", () => $(".list-sidebar").removeClass("show-sidebar"));

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
        // Пробуємо ще (20 разів максимум по 100мс = 2 секунди)
        setTimeout(() => waitForSidebar($activePage, attempt + 1), 100);
    } else {
        console.warn("Sidebar not found on this page after waiting.");
    }
}
