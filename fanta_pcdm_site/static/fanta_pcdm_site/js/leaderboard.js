function startReloadBtnCountdown() {
    let intv = -1;
    let countdownTime = 60;

    const reloadBtn = document.querySelector("#reload-btn");
    const countdownSpan = reloadBtn.querySelector(".countdown");

    reloadBtn.classList.add('disabled');
    countdownSpan.textContent = `(${countdownTime})`
    countdownSpan.classList.remove('hide');

    intv = setInterval(() => {
        let actualValue = parseInt(countdownSpan.textContent.replace("(", "").replace(")", ""));
        actualValue -= 1;

        countdownSpan.textContent = `(${actualValue})`

        if(actualValue === 0) {
            reloadBtn.classList.remove('disabled');
            countdownSpan.classList.add('hide');
            clearInterval(intv);
        }
    }, 1000);
}


function disableReloadBtn() {
    const reloadBtn = document.querySelector("#reload-btn");
    reloadBtn.classList.add('disabled');
}

function swapMeme() {
    const loaderCircle = document.querySelector(".loader-circle-3");
    const loadingMeme = document.querySelector(".loading-gif");

    if (loadingMeme.classList.contains("hide")) {
        loadingMeme.classList.remove("hide");
    } else {
        loadingMeme.classList.add("hide")
    }

    if (loaderCircle.classList.contains("hide")) {
        loaderCircle.classList.remove("hide");
    } else {
        loaderCircle.classList.add("hide")
    }
}
addEventListener("DOMContentLoaded", (event) => {
    disableReloadBtn();
    htmx.on("htmx:beforeRequest", disableReloadBtn)
    htmx.on("htmx:afterSwap", startReloadBtnCountdown)

    const loaderCircle = document.querySelector(".loader-circle-3");
    const loadingMeme = document.querySelector(".loading-gif");

    loaderCircle.addEventListener('click', swapMeme);
    loadingMeme.addEventListener('click', swapMeme);
});
