/* SpeakAjijic – main JavaScript (progressive enhancement) */

// Keyboard shortcut: Space/Left/Right to navigate flashcards
document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') {
        e.preventDefault();
        document.getElementById('flip-btn')?.click();
    } else if (e.code === 'ArrowRight' || e.code === 'ArrowDown') {
        document.getElementById('next-btn')?.click();
    } else if (e.code === 'ArrowLeft' || e.code === 'ArrowUp') {
        document.getElementById('prev-btn')?.click();
    }
});
