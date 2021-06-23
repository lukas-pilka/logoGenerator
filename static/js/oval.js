const wave = ({step, height, steps}) => {
    const path = document.createElementNS(svgNS, "path")
    let pathData = ["M 0 0", `Q ${step/2} ${-height} ${step} 0`]
    for (let i=2; i<=steps + steps % 2 - 2; i++) {
        pathData.push(`T ${step * i} 0`)
    }
    path.setAttribute("d", pathData.join(" "))
    return path
}

const wavyOval = ({width, height, steps, type = "spiky"}) => {
    console.log(width, height)
    const path = document.createElementNS(svgNS, "path")
    let pathData = []
    if (type === "perlin") {
        noise.seed(width * height * steps)
    }
    for (let i=0; i<steps; i++) {
        let x = Math.cos(Math.PI*2/steps*i)
        let y = Math.sin(Math.PI*2/steps*i)
        if (type === "perlin") {
            const noiseValue = noise.simplex2(x / 100, y / 100)
            x *= (width/2)
            y *= (height/2)
        }
        else {
            x *= (i % 2 === 0 ? width/2 + 20 : width/2)
            y *= (i % 2 === 0 ? height/2 + 20 : height/2)
        }

        if (type === "spiky") {
            if (i === 0 ) {
                pathData.push(`M ${x} ${y}`)
            }
            else {
                pathData.push(`L ${x} ${y}`)
            }
        }
        else if (["cloudyOutside", "cloudyInside"].includes(type)) {
            if (i === 0) {
                pathData.push("Q")
            }
            pathData.push(`${x} ${y}`)
        }
        else if (["wavy", "perlin"].includes(type)) {
            if (i === 0) {
                pathData.push("Q")
            }
            pathData.push(`${x} ${y}`)                    
        }
    }
    if (["cloudyOutside", "wavy", "perlin"].includes(type)) {
        pathData.splice(0, 0, `M ${pathData[pathData.length - 1]}`)
    }
    pathData.push("Z")
    path.setAttribute("d", pathData.join(" "))
    return path
}

const boxAround = (bbox, offset) => {
    const path = document.createElementNS(svgNS, "rect")
    path.setAttribute("width", bbox.width + offset*2)
    path.setAttribute("height", bbox.height + offset*2)
    return path
}