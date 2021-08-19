/*
const pages = document.querySelectorAll(".page")

pages.forEach(page => {
    page.addEventListener("click", () => {
        const target = document.querySelector(page.dataset.tabTarget)
        pages.forEach(page => {
            page.classList.remove("active")
        })
        page.classList.add("active")
        target.classList.add("active")
    })
})
*/
//identify tab clicked, save as target
//pass target as id to decorator fn
//classList.add to page