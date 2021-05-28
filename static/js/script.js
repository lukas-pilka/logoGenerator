const submitLogoGeneratorForm = (el) => {
    el.preventDefault()
    fetch("/get_logo_results", {
        method: "POST",
        body: new FormData(el.target)
    })
}