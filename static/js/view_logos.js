const standardizeColor = (name) => {
	var ctx = document.createElement("canvas").getContext("2d")
	ctx.fillStyle = name
	return ctx.fillStyle
}

const sumColor = (color) => (color._r * 0.299 + color._g * 0.587 + color._b * 0.114) * color._a //https://www.dynamsoft.com/blog/insights/image-processing/image-processing-101-color-space-conversion/

const getSecondaryColor = (name) => {
    const color = tinycolor(name)
    const summed =  sumColor(color)
    const secondary = summed > (255/2) ? tinycolor("black") : tinycolor("white")
    secondary.setAlpha(1)
    return secondary.toHex8String()
}

const buildLogos = (logos) => {
    const companyNames = ["Autokáry Plzeň", "Pizzerie Praha", "Café Šachy", "MobilMánie", "Pražské Plynovodní služby"]
    const icons = ["engine", "pizza", "chess", "mobil", "gas"]
    logos.forEach((logo, index) => {
        const primaryColor = tinycolor(logo.primaryColor.value)
        const logoWrapper = template.content.cloneNode(true)
        const logoName = logoWrapper.querySelector(".logo-name")
        const logoIcon = logoWrapper.querySelector(".logo-icon")
        logoName.textContent = companyNames[index]
        logoWrapper.querySelector(".logo-wrapper").style.fontFamily = logo.fontFamily.value
        if (primaryColor.isLight()) {
            logoWrapper.querySelector(".logo-wrapper").style.backgroundImage = `linear-gradient(${primaryColor}, ${primaryColor}, ${primaryColor.clone().darken()})` 
        }
        else {
            logoWrapper.querySelector(".logo-wrapper").style.backgroundImage = `linear-gradient(${primaryColor.clone().lighten().lighten()}, ${primaryColor}, ${primaryColor})` 
        }
        const secondaryColor = getSecondaryColor(logo.primaryColor.value)
        logoName.style.color = secondaryColor
        if (Math.abs(sumColor(tinycolor(logo.primaryColor.value)) - sumColor(tinycolor(secondaryColor))) > 255*.8) {
            const shadow = document.createElement("div")
            shadow.className = "logo-name--shadow"
            shadow.textContent = companyNames[index]
            logoWrapper.querySelector(".logo-wrapper").appendChild(shadow)
            shadow.style.color = logo.primaryColor.value
            if (["Roboto Condensed", "Roboto"].includes(logo.fontFamily.value)) {
                logoName.classList.add("lines")
                logoName.style.borderColor = secondaryColor
            }
        }
        logosWrapper.appendChild(logoWrapper)
        const bbox = logoName.getBoundingClientRect()
        const fontScaleRatio = 200/bbox.width
        logosWrapper.lastElementChild.firstElementChild.style.fontSize = `${fontScaleRatio}em`
        // fetch(`/icon/${icons[index]}`)
        // .then(response => response.json())
        // .then(data => {
        //     logoIcon.innerHTML = data.icon
        //     logoIcon.style.fill = secondaryColor
        //     logoIcon.style.marginBottom = (1 - fontScaleRatio) + "em"
        // })
    })
    // icons.forEach((icon, index) => {
    //     fetch(`/icon/${icon}`)
    //     .then(response => response.json())
    //     .then(svg => {
    //         const logoIcon = logosWrapper.children[index].querySelector(".logo-icon")
    //         logoIcon.innerHTML = svg.icon
    //         logoIcon.style = `fill: ${};`
    //         // logoIcon.style = `background: red;`
    //     })
    // })
    // tinycolor(logoIcon.parentNode.style.backgroundColor).darken(25).toString()
}

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
    let fonts = []
    logos.forEach(logo => {
        fonts.push(logo.fontFamily.value)
    })
    WebFont.load({
        google: {families: fonts},
        active: () => {buildLogos(logos)}
    })
})

