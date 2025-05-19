$(function () {
    // Creating a button for toggling the sidebar on mobile devices
    const toggleBtn = $(`<button class="custom-toggle-sidebar"><div class="burger-icon"></div></button>`)
    toggleBtn.on('click', () => $('.list-sidebar').toggleClass("show-sidebar"))
    $(".navbar").prepend(toggleBtn)

    // Adding an arrow to close the sidebar
    const backBtn = $(`<button class="custom-close-sidebar"><div class="arrow-back-icon"></div></div>`);
    backBtn.on('click', () => $('.list-sidebar').removeClass("show-sidebar"));
    
    // Adding a top part of the navbar
    const sidebarTop = $(`
        <div class="sidebar-top">
            <a href="/app"><img src="/files/energy-masters-logo.png" alt="App Logo" class="sidebar-top-logo"></a>
        </div>
    `)
    sidebarTop.prepend(backBtn);
    
    $(".list-sidebar").prepend(sidebarTop);

    // Automaticly hide sidebar when user clicks on a link
    $(".layout-side-section").on("click", "a", function () {
        setTimeout(() => $(".list-sidebar").removeClass("show-sidebar"), 200);
    });
});