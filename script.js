const bgContainer = document.getElementById('bg-container');
const mirceaLayer = document.getElementById('mircea-layer');

function loadNewImage() {
  const img = document.createElement('img');
  img.src = 'https://source.unsplash.com/random/1920x1080?sig=' + Math.random();
  img.onload = () => {
    bgContainer.innerHTML = '';
    bgContainer.appendChild(img);
  };
}

function generateMircea() {
  mirceaLayer.innerHTML = '';
  for (let i = 0; i < 150; i++) {
    const span = document.createElement('span');
    span.className = 'mircea';
    span.textContent = 'Mircea Papusoi';
    span.style.top = Math.random() * 100 + '%';
    span.style.left = Math.random() * 100 + '%';
    span.style.fontSize = (10 + Math.random() * 20) + 'px';
    span.style.opacity = (0.4 + Math.random() * 0.6).toFixed(2);
    span.style.animationDuration = (3 + Math.random() * 5).toFixed(2) + 's';
    mirceaLayer.appendChild(span);
  }
}

setInterval(loadNewImage, 1000);
setInterval(generateMircea, 8000);
loadNewImage();
generateMircea();

setTimeout(() => {
  window.location.href = 'about.html';
}, 30000);