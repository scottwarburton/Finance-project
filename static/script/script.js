
const pages = document.querySelectorAll(".page")
const pageContents = document.querySelectorAll("pageContent")

pages.forEach(page => {
    page.addEventListener("click", () => {
        const target = document.querySelector(page.dataset.tabTarget)
        pageContents.forEach(pageContent => {
            pageContent.classList.remove("active")
        })
        pages.forEach(page => {
            page.classList.remove("active")
        })
        page.classList.add("active")
        target.classList.add("active")
    })
})