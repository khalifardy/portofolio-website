// Typing animation
const roles = [
    "Ideas Growing Under the Sun 🌱",
    "Different Perspectives, One Vision 📖",
    "Where Wisdom Meets Innovation 🦉",
    "AI & Machine Learning 🤖",
    "Amateur Astronomer 🔭",
    "Science & Philosophy ⚛️"
];

let roleIndex = 0;
let charIndex = 0;
let isDeleting = false;
const typingElement = document.getElementById('typing');

function type() {
    if (!typingElement) return;
    
    const currentRole = roles[roleIndex];
    
    if (isDeleting) {
        typingElement.textContent = currentRole.substring(0, charIndex - 1);
        charIndex--;
    } else {
        typingElement.textContent = currentRole.substring(0, charIndex + 1);
        charIndex++;
    }
    
    if (!isDeleting && charIndex === currentRole.length) {
        isDeleting = true;
        setTimeout(type, 2000);
    } else if (isDeleting && charIndex === 0) {
        isDeleting = false;
        roleIndex = (roleIndex + 1) % roles.length;
        setTimeout(type, 500);
    } else {
        setTimeout(type, isDeleting ? 50 : 100);
    }
}

// Leaf falling animation
function createLeaf() {
    const leaf = document.createElement('div');
    leaf.className = 'leaf';
    leaf.innerHTML = '🍃';
    leaf.style.left = Math.random() * 100 + '%';
    leaf.style.animationDuration = (Math.random() * 3 + 7) + 's';
    document.getElementById('leaves')?.appendChild(leaf);
    
    setTimeout(() => leaf.remove(), 10000);
}

if(document.getElementById('leaves')) {
    setInterval(createLeaf, 2000);
}

// Create stars
function createStars() {
    const starsContainer = document.getElementById('stars');
    if (!starsContainer) return;
    
    const numStars = 100;
    
    for (let i = 0; i < numStars; i++) {
        const star = document.createElement('div');
        star.className = 'star';
        star.style.left = Math.random() * 100 + '%';
        star.style.top = Math.random() * 100 + '%';
        star.style.animationDelay = Math.random() * 4 + 's';
        starsContainer.appendChild(star);
    }
}

// Initialize
document.addEventListener('DOMContentLoaded', () => {
    createStars();
    type();
});