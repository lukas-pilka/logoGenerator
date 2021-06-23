const diagonal = (width, height) => {
    return Math.sqrt(Math.pow(width, 2) + Math.pow(height, 2))
}

const elementDiagonal = (box) => {
    return diagonal(box.width, box.height)
}