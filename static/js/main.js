let nav_btn = document.querySelector('#nav-btn')
let nav = document.querySelector('nav')
let toggle = false
nav_btn.addEventListener('click', () => {
    if (!toggle) {
        toggle = true
        nav.style.top = '50px'
    } else {
        toggle = false
        nav.style.top = '-100%'
    }
})

let btns = document.querySelectorAll('nav ul li a')
btn = btns[btns.length - 1]
btn.innerHTML = btn.innerHTML + ' <i class="fas fa-sign-out-alt" style="position: relative; top: 1px;"></i>'