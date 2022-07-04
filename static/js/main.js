let nav_btn = document.querySelector('#nav-btn')
let nav = document.querySelector('nav')
let toggle = false
nav_btn.addEventListener('click', () => {
    if (!toggle) {
        toggle = true
        nav.style.top = '50px'
        nav_btn.innerHTML = '<i class="fas fa-times" style="font-size: 2rem; position: relative; top: 3px; transition: linear 0.2s;"></i>'
    } else {
        toggle = false
        nav.style.top = '-100%'
        nav_btn.innerHTML = '<i class="fas fa-bars"></i>'
    }
})

let btns = document.querySelectorAll('nav ul li a')
btn = btns[btns.length - 1]
btn.innerHTML = btn.innerHTML + ' <i class="fas fa-sign-out-alt" style="position: relative; top: 1px;"></i>'

let nidx = '12345'
let nid = document.querySelector('.documents #nid')
let check = document.querySelector('.documents #check')
if (nid) {
    nid.addEventListener('change', (event) => {
        nid.textContent = `${event.target.value}`
        if (nid.textContent != nidx) {
            check.style.display = 'block'
            check.innerHTML = '<i class="fas fa-times-circle"></i>'
            check.classList.remove('good')
            check.classList.add('bad')
        } else if (nid.textContent == nidx) {
            check.style.display = 'block'
            check.innerHTML = '<i class="fas fa-check-circle"></i>'
            check.classList.remove('bad')
            check.classList.add('good')
        } else {
            check.style.display = 'none'
        }
    })
}