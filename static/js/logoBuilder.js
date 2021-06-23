svgNS = "http://www.w3.org/2000/svg"

const buildLogo = (wrapper, logoData) => {
    console.log("hi")
    return
    const svg = document.createElementNS(svgNS, "svg")
    svg.style.background = logoData.primaryColor.value
    svg.setAttribute("height", 300)
    svg.setAttribute("width", 300)
    // document.getElementById("logos-wrapper").appendChild(svg)
    wrapper.appendChild(svg)
    const text = logoData.svg
    svg.appendChild(text)
    let textBox = text.getBBox()
    const sf = 200/textBox.width // scaling factor
    text.setAttribute("transform", `translate(150 150) scale(${sf})`)    
    textBox = text.getBoundingClientRect()
    const svgBox = svg.getBoundingClientRect()
    textBox.x -= svgBox.x
    textBox.y -= svgBox.y

    if (logoData.oval.value) {
        const diagonal = elementDiagonal(textBox)
        shape = wavyOval({
            width: logoData.oval.value.adjustToContent ? textBox.width/Math.sqrt(2) * 2 : diagonal + 25,
            height: logoData.oval.value.adjustToContent ? textBox.height/Math.sqrt(2) * 2  : diagonal + 25,
            widthSpike: logoData.oval.value.widthSpike,
            heightSpike: logoData.oval.value.heightSpike,
            type: logoData.oval.value.type,
            steps: logoData.oval.value.steps
        })
        shape.setAttribute("transform", "translate(150 150)")
        shape.setAttribute("fill", logoData.oval.value.fill)
        shape.setAttribute("stroke", logoData.oval.value.stroke)
        shape.setAttribute("stroke-width", logoData.oval.value.strokeWidth)
        shape.setAttribute("stroke-linejoin", logoData.oval.value.strokeLineJoin)
        shape.setAttribute("stroke-miterlimit", 0)
        svg.insertBefore(shape, svg.firstElementChild)
    }

    if (logoData.textDecorationWavy.value) {
        const shape = wave({
            step: logoData.textDecorationWavy.value.step,
            height: logoData.textDecorationWavy.value.height,
            steps: textBox.width/logoData.textDecorationWavy.value.step
        })
        shape.setAttribute("fill", "none")
        shape.setAttribute("stroke", "black")
        shape.setAttribute("stroke-width", logoData.textDecorationWavy.value.strokeWidth)
        if (logoData.textDecorationWavy.value.top) {
            const shapeTop = shape.cloneNode()
            svg.appendChild(shapeTop)
            shapeTop.setAttribute("transform", `translate(${150 - shapeTop.getBBox().width/2} ${textBox.y - shapeTop.getBBox().height * 2})`)      
        }
        if (logoData.textDecorationWavy.value.bottom) {
            const shapeBottom = shape.cloneNode()
            svg.appendChild(shapeBottom)
            shapeBottom.setAttribute("transform", `translate(${150 - shapeBottom.getBBox().width/2} ${textBox.y + textBox.height + shapeBottom.getBBox().height * 2})`)      
        }
    }
    if (logoData?.boxAround) {
        const box = boxAround(textBox, logoData.boxAround.value.offset + logoData.boxAround.value.strokeWidth/2)
        svg.insertBefore(box, text)
        box.setAttribute("fill", logoData.boxAround.value.fill ? logoData.boxAround.value.fill : "transparent" )
        box.setAttribute("stroke", logoData.boxAround.value.stroke ? logoData.boxAround.value.stroke : "transparent" )
        box.setAttribute("transform", `translate(${textBox.x - logoData.boxAround.value.offset - logoData.boxAround.value.strokeWidth/2} ${textBox.y - logoData.boxAround.value.offset-logoData.boxAround.value.strokeWidth/2})`)
        box.setAttribute("stroke-width", logoData.boxAround.value.strokeWidth)
        box.setAttribute("stroke-alignment", "outside")
    }
}