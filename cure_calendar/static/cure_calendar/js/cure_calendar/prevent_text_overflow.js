// Wait for document to be fully loaded
window.addEventListener('load', () => {
    document.querySelectorAll('.line-container__stop').forEach(element => {
        const currentMarginRight = getComputedStyle(element).marginRight;
        const availableWidth = element.parentElement.offsetWidth - parseFloat(currentMarginRight);
        const actualWidth = element.offsetWidth;
        
        if (actualWidth > availableWidth) {
            element.style.left = '1px';
            element.style.marginRight = '0px';
        }
    });
});