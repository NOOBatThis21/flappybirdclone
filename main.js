// ====================
// Flappy Bird Clone
// ====================
//
// This script handles all game logic: drawing, physics, input,
// pipe generation, collision detection, and scoring.
// Copy directly into your project. Edit constants as needed.
//
// ====================

// 1. Get canvas and context
const canvas = document.getElementById('game-canvas');
const ctx = canvas.getContext('2d');

// 2. Game constants (tweak these to change difficulty/feel)
const GRAVITY = 0.5;       // Downward acceleration per frame
const JUMP_STRENGTH = -8;  // Upward velocity when "flap" happens
const PIPE_SPEED = 2;      // How fast pipes move left
const PIPE_WIDTH = 50;     // Width of each pipe
const PIPE_GAP = 140;      // Vertical gap between top and bottom pipes
const PIPE_INTERVAL = 1500; // Milliseconds between pipe spawns
const BIRD_SIZE = 30;      // Bird width & height
const FLOOR_HEIGHT = 80;   // Height of the ground area at bottom

// 3. Bird object
const bird = {
  x: 80,                   // Horizontal position (fixed)
  y: canvas.height / 2,    // Vertical position (starts middle)
  width: BIRD_SIZE,
  height: BIRD_SIZE,
  velocity: 0,             // Current vertical velocity
  rotation: 0,             // For drawing tilt (in radians)
  alive: true,
};

// 4. Pipe class
class Pipe {
  constructor(canvasWidth, canvasHeight) {
    // Starting X is just off the right edge
    this.x = canvasWidth;
    this.width = PIPE_WIDTH;

    // Randomly choose where the gap will start
    const gapPosition = Math.random() * (canvasHeight - PIPE_GAP - FLOOR_HEIGHT - 40) + 20;
    this.topHeight = gapPosition;
    this.bottomY = gapPosition + PIPE_GAP;

    this.passed = false; // Track if bird has passed this pipe
  }

  // Draw top and bottom rectangles
  draw(ctx) {
    ctx.fillStyle = '#0f0'; // Green pipes

    // Top pipe
    ctx.fillRect(this.x, 0, this.width, this.topHeight);

    // Bottom pipe
    ctx.fillRect(
      this.x,
      this.bottomY,
      this.width,
      canvas.height - this.bottomY - FLOOR_HEIGHT
    );
  }

  // Move pipe leftward
  update() {
    this.x -= PIPE_SPEED;
  }
}

// 5. Game state
let pipes = [];
let lastPipeTime = Date.now();
let score = 0;

// 6. Ground image (we’ll draw a simple brown rectangle)
function drawGround() {
  ctx.fillStyle = '#8b4513'; // SaddleBrown for ground
  ctx.fillRect(0, canvas.height - FLOOR_HEIGHT, canvas.width, FLOOR_HEIGHT);
}

// 7. Draw the bird with rotation based on velocity
function drawBird() {
  ctx.save();
  // Move origin to bird center to rotate around center
  ctx.translate(bird.x + bird.width / 2, bird.y + bird.height / 2);
  // Rotate by small amount based on velocity
  const maxRotation = Math.PI / 4; // 45 degrees max tilt
  const rotationFactor = bird.velocity / 10;
  bird.rotation = Math.min(Math.max(rotationFactor, -maxRotation), maxRotation);
  ctx.rotate(bird.rotation);

  // Draw bird as yellow rectangle with red eye
  ctx.fillStyle = '#ff0'; // Yellow
  ctx.fillRect(-bird.width / 2, -bird.height / 2, bird.width, bird.height);

  // Draw eye (simple red circle)
  ctx.beginPath();
  ctx.arc(bird.width / 4, -bird.height / 8, 4, 0, 2 * Math.PI);
  ctx.fillStyle = '#f00'; // Red eye
  ctx.fill();
  ctx.closePath();

  ctx.restore();
}

// 8. Handle user input (click or spacebar to flap)
function flap() {
  if (!bird.alive) return;
  bird.velocity = JUMP_STRENGTH;
}

// Mouse or touch
canvas.addEventListener('mousedown', flap);
canvas.addEventListener('touchstart', (e) => {
  e.preventDefault();
  flap();
});

// Spacebar
document.addEventListener('keydown', (e) => {
  if (e.code === 'Space') {
    flap();
  }
});

// 9. Check for collisions (bird vs. ground or pipes)
function checkCollision() {
  // Ground collision
  if (bird.y + bird.height > canvas.height - FLOOR_HEIGHT) {
    return true;
  }

  // Ceiling collision
  if (bird.y < 0) {
    return true;
  }

  // Pipe collisions
  for (let pipe of pipes) {
    // Bird’s bounding box
    const birdLeft = bird.x;
    const birdRight = bird.x + bird.width;
    const birdTop = bird.y;
    const birdBottom = bird.y + bird.height;

    // Top pipe bounding box
    const topPipeLeft = pipe.x;
    const topPipeRight = pipe.x + pipe.width;
    const topPipeTop = 0;
    const topPipeBottom = pipe.topHeight;

    // Bottom pipe bounding box
    const bottomPipeLeft = pipe.x;
    const bottomPipeRight = pipe.x + pipe.width;
    const bottomPipeTop = pipe.bottomY;
    const bottomPipeBottom = canvas.height - FLOOR_HEIGHT;

    // Check overlap with top pipe
    if (
      birdRight > topPipeLeft &&
      birdLeft < topPipeRight &&
      birdTop < topPipeBottom
    ) {
      return true;
    }

    // Check overlap with bottom pipe
    if (
      birdRight > bottomPipeLeft &&
      birdLeft < bottomPipeRight &&
      birdBottom > bottomPipeTop
    ) {
      return true;
    }
  }

  return false;
}

// 10. Main game loop
function gameLoop() {
  // Clear the entire canvas
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  // Draw and update pipes
  for (let i = pipes.length - 1; i >= 0; i--) {
    const pipe = pipes[i];
    pipe.update();
    pipe.draw(ctx);

    // Check if bird has passed this pipe (score condition)
    if (!pipe.passed && bird.x > pipe.x + pipe.width) {
      pipe.passed = true;
      score += 1;
      updateScore();
    }

    // Remove pipes that have moved off screen
    if (pipe.x + pipe.width < 0) {
      pipes.splice(i, 1);
    }
  }

  // Add a new pipe at regular intervals
  if (Date.now() - lastPipeTime > PIPE_INTERVAL) {
    pipes.push(new Pipe(canvas.width, canvas.height));
    lastPipeTime = Date.now();
  }

  // Bird physics: apply gravity, update position
  bird.velocity += GRAVITY;
  bird.y += bird.velocity;

  // Draw the bird
  drawBird();

  // Draw the ground
  drawGround();

  // Check for collision
  if (checkCollision()) {
    bird.alive = false;
    showGameOver();
    return; // Stop updating once game is over
  }

  // Continue loop
  requestAnimationFrame(gameLoop);
}

// 11. Update score display
function updateScore() {
  const scoreDisplay = document.getElementById('score-display');
  scoreDisplay.textContent = `Score: ${score}`;
}

// 12. Display “Game Over” text and reset option
function showGameOver() {
  ctx.fillStyle = 'rgba(0, 0, 0, 0.5)';
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = '#fff';
  ctx.font = '48px Arial';
  ctx.textAlign = 'center';
  ctx.fillText('Game Over', canvas.width / 2, canvas.height / 2 - 20);

  ctx.font = '24px Arial';
  ctx.fillText(
    `Final Score: ${score}`,
    canvas.width / 2,
    canvas.height / 2 + 20
  );

  ctx.font = '18px Arial';
  ctx.fillText(
    'Click or press Space to restart',
    canvas.width / 2,
    canvas.height / 2 + 60
  );

  // Restart on next click or keypress
  function restartHandler() {
    resetGame();
    canvas.removeEventListener('mousedown', restartHandler);
    document.removeEventListener('keydown', restartHandler);
  }
  canvas.addEventListener('mousedown', restartHandler);
  document.addEventListener('keydown', (e) => {
    if (e.code === 'Space') restartHandler();
  });
}

// 13. Reset everything to initial state
function resetGame() {
  bird.y = canvas.height / 2;
  bird.velocity = 0;
  bird.alive = true;
  pipes = [];
  score = 0;
  updateScore();
  lastPipeTime = Date.now();
  gameLoop();
}

// 14. Initialize score display and start the loop
updateScore();
gameLoop();
