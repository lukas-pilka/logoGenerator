function voterPass() {
    let d = new Date();
    let xSecs = 10 // * Duration in seconds
    d.setTime(d.getTime() + (xSecs * 1000));
    let expires = "expires=" + d.toGMTString();
    document.cookie = "voterPass=True;" + expires;
}

const submitLogoGeneratorForm = (el) => {
    el.preventDefault()
    fetch("/get_logo_results", {
        method: "POST",
        body: new FormData(el.target)
    })
}