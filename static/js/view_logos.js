const svgNS = "http://www.w3.org/2000/svg"


const companyNames = ["Pizzeria", "Pa", "Good Office", "Computeři"]
const template = document.getElementById("logo-wrapper-template")
const logosWrapper = document.getElementById("logos-wrapper")
const data = fetch("/get_logo_results?static=1", {
    method: "POST",
    credentials: 'same-origin',
    headers: {
        'Content-Type': 'application/json',
    },
    body: new FormData()
})
.then(response => response.json())
.then(logos => {
    logos.forEach((logo, index) => {
        fetch(`/svg/${logo.fontFamily.value}/${logo.initials.value ? companyNames[index] : companyNames[index]}`)
        .then(response => response.json())
        .then(data => {
            const path = document.createElementNS(svgNS, "path")
            path.setAttribute("d", data.svg)
            logo.svg = path
            buildLogo(logo)
        })
    })
})

