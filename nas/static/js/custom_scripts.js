function toggleProfileMenu() {
    if (dropdownUser.classList.contains('show')) {
        dropdownUser.classList.remove('show');
        dropdownMenu.classList.remove('show');
    } else {
        dropdownUser.classList.add('show');
        dropdownMenu.classList.add('show');
        dropdownMenu.style = 'position: absolute; inset: 0px auto auto 0px; margin: 0px; transform: translate(-5rem, 2.5rem);';
    }
}