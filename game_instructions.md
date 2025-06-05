# Game Instructions and Customization

## How to Play

1. Open `index.html` in your browser (or serve via a local HTTP server).
2. The bird starts in mid-air, falling under gravity.
3. **Click** anywhere on the canvas (or press **Spacebar**) to make the bird “flap” upward.
4. Navigate the bird through oncoming green pipes.
5. Each time you pass between a pipe pair, you earn 1 point.
6. The game ends when:
   - The bird hits the ground (bottom brown rectangle).
   - The bird collides with a pipe.
7. On “Game Over,” click (or press Space) to restart from zero.

## Tweak Game Variables

Open `main.js` and find the top section labeled **Game constants**. For example:

```js
// Game constants (edit to tweak difficulty)
const GRAVITY = 0.5;
const JUMP_STRENGTH = -8;
const PIPE_SPEED = 2;
const PIPE_WIDTH = 50;
const PIPE_GAP = 140;
const PIPE_INTERVAL = 1500; // ms between pipe spawns
const BIRD_SIZE = 30;
const FLOOR_HEIGHT = 80;
